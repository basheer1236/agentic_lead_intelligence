import os
import json
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy import text

from app.config.settings import settings
from app.ui.pipeline_runner import runner
from app.storage.database import SessionLocal, reset_db_engine
from app.export.excel_exporter import ExcelExporter

from contextlib import asynccontextmanager


def _init_db_in_background():
    try:
        from app.storage.database import engine
        from app.storage.base import Base
        import app.storage.models
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Instant non-blocking server startup
    asyncio.create_task(asyncio.to_thread(_init_db_in_background))
    yield


app = FastAPI(title="Agentic Lead Intelligence Console", lifespan=lifespan)

TEMPLATE_PATH = Path(__file__).parent / "templates" / "index.html"
EXPORTS_DIR = Path("data/exports")
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


class RunRequest(BaseModel):
    batch_size: int = 5
    single_test_mode: bool = False


StartRequest = RunRequest  # Backward-compatible alias


class SettingsUpdateRequest(BaseModel):
    database_url: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None


@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "Agentic Lead Intelligence Console"}


@app.get("/", response_class=HTMLResponse)
async def get_index():
    if not TEMPLATE_PATH.exists():
        raise HTTPException(status_code=404, detail="Dashboard template not found.")
    return TEMPLATE_PATH.read_text(encoding="utf-8")


@app.post("/api/pipeline/run")
@app.post("/api/pipeline/start")
async def run_pipeline(req: RunRequest):
    success, msg = runner.start(batch_size=req.batch_size, single_test_mode=req.single_test_mode)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "status": runner.get_snapshot()["status"]}


@app.post("/api/pipeline/abort")
@app.post("/api/pipeline/stop")
async def abort_pipeline():
    success, msg = runner.cancel()
    return {"success": success, "message": msg, "status": runner.get_snapshot()["status"]}


@app.get("/api/pipeline/status")
async def get_status():
    return runner.get_snapshot()


@app.get("/api/pipeline/stream")
async def stream_pipeline_events(request: Request):
    q = runner.subscribe()

    async def event_generator():
        try:
            # Send initial snapshot
            init_data = json.dumps({"type": "status", "data": runner.get_snapshot()})
            yield f"data: {init_data}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Non-blocking pull with small sleep
                    event = q.get_nowait()
                    yield f"data: {json.dumps(event)}\n\n"
                except Exception:
                    await asyncio.sleep(0.5)
        finally:
            runner.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/exports")
async def list_exports():
    results = []
    for f in EXPORTS_DIR.glob("*.xlsx"):
        stat = f.stat()
        results.append({
            "filename": f.name,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": stat.st_mtime,
        })
    return results


@app.get("/api/exports/download/{filename}")
async def download_export(filename: str):
    # Sanitize filename
    safe_name = Path(filename).name
    file_path = EXPORTS_DIR / safe_name

    # If file doesn't exist yet on disk, generate it dynamically from the database
    if not file_path.exists():
        db = SessionLocal()
        try:
            exporter = ExcelExporter()
            file_path = exporter.export(db, filename=safe_name)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to generate export: {exc}")
        finally:
            db.close()

    return FileResponse(
        path=file_path,
        filename=safe_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/api/leads/preview")
async def get_leads_preview():
    db = SessionLocal()
    try:
        query = text("""
            SELECT 
                p.project_name,
                COALESCE(p.designer_name, d.designer_name) AS designer_name,
                COALESCE(p.designer_studio, d.studio_name) AS designer_studio,
                p.location,
                p.homeowner_name,
                s.lead_score,
                s.rug_opportunity_score
            FROM projects p
            LEFT JOIN designers d ON p.designer_id = d.id
            LEFT JOIN scores s ON p.id = s.project_id
            ORDER BY p.id DESC
            LIMIT 25
        """)
        rows = db.execute(query).mappings().all()
        return [dict(r) for r in rows]
    except Exception as exc:
        return []
    finally:
        db.close()


@app.get("/api/settings")
async def get_settings():
    return {
        "database_url": settings.database_url,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "has_api_key": bool(settings.llm_api_key),
    }


@app.post("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    env_path = Path(".env")
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    def update_key(key: str, val: str):
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={val}"
                found = True
                break
        if not found:
            lines.append(f"{key}={val}")

    if req.database_url is not None:
        update_key("DATABASE_URL", req.database_url)
        settings.database_url = req.database_url
        try:
            reset_db_engine(req.database_url)
        except Exception:
            pass

    if req.llm_provider is not None:
        update_key("LLM_PROVIDER", req.llm_provider)
        settings.llm_provider = req.llm_provider

    if req.llm_model is not None:
        update_key("LLM_MODEL", req.llm_model)
        settings.llm_model = req.llm_model

    if req.llm_api_key is not None and req.llm_api_key.strip():
        update_key("LLM_API_KEY", req.llm_api_key.strip())
        settings.llm_api_key = req.llm_api_key.strip()

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"success": True, "message": "Settings updated and saved to .env"}


def main():
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print("\n" + "=" * 65)
    print("  AGENTIC LEAD INTELLIGENCE - EXECUTIVE DASHBOARD")
    print(f"  Server starting at: http://{host}:{port}")
    print("=" * 65 + "\n")
    uvicorn.run("app.ui.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
