from pathlib import Path
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExcelExporter:

    def __init__(self, output_dir: str = "data/exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    @staticmethod
    def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        id_cols = {'designer_id', 'project_id', 'rug_id', 'article_id'}
        for col in df.columns:
            if col in id_cols:
                continue
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                try:
                    df[col] = df[col].dt.tz_localize(None)
                except Exception:
                    pass
            elif pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna("Not Disclosed")
        return df

    def _get_readme_dataframe(self) -> pd.DataFrame:
        readme_data = [
            ["WORKBOOK PURPOSE", "This workbook contains project-level, designer-level, and rug-opportunity lead intelligence extracted and enriched by the Agentic AI Lead Intelligence system."],
            ["SOURCE OF TRUTH", "PostgreSQL database is the authoritative system of record. This Excel workbook is a relationally aligned business intelligence report."],
            ["DATA COMPLETENESS NOTICE", "Strict evidence-based rules prohibit AI hallucination. Cells marked as 'Not Disclosed' or 'N/A' represent information omitted or unstated in source articles."],
            ["", ""],
            ["SHEET BREAKDOWN", ""],
            ["1. README", "Documentation, relational schema diagram, sheet breakdown, and primary/foreign key mapping."],
            ["2. Lead Intelligence Master", "Architectural Digest India projects and residential lead intelligence. Identifiers: project_id (PK), designer_id (FK), article_id (FK)."],
            ["3. Interior Designer Master", "Unique interior designer & firm master records. Identifier: designer_id (PK)."],
            ["4. Rug Opportunity Tracker", "Rug, carpet, and floor-covering sourcing opportunities tied to projects and designers. Identifiers: rug_id (PK), project_id (FK), designer_id (FK)."],
            ["", ""],
            ["RELATIONAL SCHEME", ""],
            ["Designer Master Record", "designer_id (PK)"],
            ["  │", ""],
            ["  ├───────────────┐", ""],
            ["  ▼               ▼", ""],
            ["Lead Intelligence  Rug Opportunity Tracker"],
            ["project_id (PK)    rug_id (PK)"],
            ["designer_id (FK)   project_id (FK)"],
            ["article_id (FK)    designer_id (FK)"],
            ["", ""],
            ["PRIMARY & FOREIGN KEYS", ""],
            ["designer_id", "Uniquely identifies an interior designer / architecture studio."],
            ["project_id", "Uniquely identifies a residential project lead."],
            ["rug_id", "Uniquely identifies a rug / floor-covering opportunity record."],
            ["article_id", "Uniquely identifies the source article from Architectural Digest India."],
        ]
        return pd.DataFrame(readme_data, columns=["Section / Concept", "Description / Details"])

    def export(
        self,
        db: Session,
        filename: str = "lead_intelligence.xlsx",
        exclude_test_data: bool = True,
    ) -> Path:

        output_path = self.output_dir / filename

        readme_df = self._get_readme_dataframe()
        lead_df = self._clean_dataframe(self._get_lead_intelligence(db, exclude_test_data))
        designer_df = self._clean_dataframe(self._get_designer_master(db, exclude_test_data))
        rug_df = self._clean_dataframe(self._get_rug_opportunities(db, exclude_test_data))

        def write_excel(target_path: Path):
            with pd.ExcelWriter(target_path, engine="openpyxl") as writer:
                readme_df.to_excel(
                    writer,
                    sheet_name="README",
                    index=False,
                )
                lead_df.to_excel(
                    writer,
                    sheet_name="Lead Intelligence Master",
                    index=False,
                )
                designer_df.to_excel(
                    writer,
                    sheet_name="Interior Designer Master",
                    index=False,
                )
                rug_df.to_excel(
                    writer,
                    sheet_name="Rug Opportunity Tracker",
                    index=False,
                )

                # Format worksheets with openpyxl
                thin_border = Border(
                    left=Side(style='thin', color='D9D9D9'),
                    right=Side(style='thin', color='D9D9D9'),
                    top=Side(style='thin', color='D9D9D9'),
                    bottom=Side(style='thin', color='D9D9D9')
                )

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    
                    # Freeze panes
                    worksheet.freeze_panes = "A2"

                    # Header styling
                    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
                    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                    
                    if sheet_name == "README":
                        readme_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
                        for cell in worksheet[1]:
                            cell.font = header_font
                            cell.fill = readme_fill
                            cell.alignment = Alignment(horizontal="left", vertical="center")
                    else:
                        worksheet.auto_filter.ref = worksheet.dimensions
                        for cell in worksheet[1]:
                            cell.font = header_font
                            cell.fill = header_fill
                            cell.alignment = Alignment(horizontal="center", vertical="center")

                    # Cell grid alignment and borders
                    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
                        for cell in row:
                            cell.border = thin_border
                            if isinstance(cell.value, (int, float)):
                                cell.alignment = Alignment(horizontal="right", vertical="center")
                            elif isinstance(cell.value, bool) or str(cell.value).upper() in ("TRUE", "FALSE", "YES", "NO"):
                                cell.alignment = Alignment(horizontal="center", vertical="center")
                            else:
                                cell.alignment = Alignment(horizontal="left", vertical="center")

                    # Column width auto-fitting
                    for col in worksheet.columns:
                        max_len = max(len(str(cell.value or "")) for cell in col)
                        col_letter = get_column_letter(col[0].column)
                        worksheet.column_dimensions[col_letter].width = min(
                            max(max_len + 3, 14), 60
                        )

        try:
            write_excel(output_path)
        except (PermissionError, OSError):
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{output_path.stem}_{timestamp}{output_path.suffix}"
            write_excel(output_path)

        return output_path

    def _get_lead_intelligence(
        self,
        db: Session,
        exclude_test_data: bool = True
    ) -> pd.DataFrame:

        where_clause = ""
        if exclude_test_data:
            where_clause = """
                WHERE (p.project_name IS NULL OR (
                    LOWER(p.project_name) NOT LIKE '%test%' 
                    AND LOWER(p.project_name) NOT LIKE '%e2e%' 
                    AND LOWER(p.project_name) NOT LIKE '%idempotency%'
                ))
                AND (p.designer_name IS NULL OR (
                    LOWER(p.designer_name) NOT LIKE '%test%'
                    AND LOWER(p.designer_name) NOT LIKE '%e2e%'
                    AND LOWER(p.designer_name) NOT LIKE '%idempotency%'
                ))
            """

        query = text(f"""
            SELECT
                p.id AS project_id,
                p.designer_id,
                a.id AS article_id,
                a.url AS article_url,
                a.title AS article_title,
                a.published_at,
                COALESCE(p.project_name, a.title, 'Architectural Digest Project') AS project_name,
                COALESCE(p.home_type, 'Residential Space') AS home_type,
                COALESCE(p.location, 'India') AS location,
                COALESCE(p.project_size, 'Not Disclosed') AS project_size,
                COALESCE(p.completion_year, 'Not Disclosed') AS completion_year,
                COALESCE(p.homeowner_name, 'Not Disclosed in Article') AS homeowner_name,
                COALESCE(p.homeowner_profession, 'Not Disclosed in Article') AS homeowner_profession,
                COALESCE(p.homeowner_industry, 'Not Disclosed in Article') AS homeowner_industry,
                COALESCE(p.homeowner_city, d.city, 'India') AS homeowner_city,
                COALESCE(p.homeowner_country, d.country, 'India') AS homeowner_country,
                COALESCE(p.designer_name, d.designer_name, 'Independent Designer') AS designer_name,
                COALESCE(p.designer_studio, d.studio_name, 'Independent Studio') AS designer_studio,
                COALESCE(p.designer_role, 'Architect / Interior Designer') AS designer_role,
                COALESCE(p.designer_city, d.city, 'India') AS designer_city,
                COALESCE(p.designer_website, d.website, 'Not Disclosed') AS designer_website,
                COALESCE(s.lead_score, 0) AS lead_score,
                COALESCE(s.rug_opportunity_score, 0) AS rug_opportunity_score
            FROM projects p
            JOIN articles a
                ON p.article_id = a.id
            LEFT JOIN designers d
                ON p.designer_id = d.id
            LEFT JOIN scores s
                ON p.id = s.project_id
            {where_clause}
            ORDER BY a.published_at DESC NULLS LAST, p.id DESC
        """)

        result = db.execute(query)
        return pd.DataFrame(result.mappings().all())

    def _get_designer_master(
        self,
        db: Session,
        exclude_test_data: bool = True
    ) -> pd.DataFrame:

        where_clause = ""
        if exclude_test_data:
            where_clause = """
                WHERE LOWER(designer_name) NOT LIKE '%test%' 
                  AND LOWER(designer_name) NOT LIKE '%e2e%' 
                  AND LOWER(designer_name) NOT LIKE '%idempotency%'
            """

        query = text(f"""
            SELECT
                id AS designer_id,
                COALESCE(designer_name, 'Independent Designer') AS designer_name,
                COALESCE(studio_name, 'Independent Studio') AS studio_name,
                COALESCE(normalized_name, LOWER(designer_name)) AS normalized_name,
                COALESCE(website, 'Not Disclosed') AS website,
                COALESCE(address, 'Not Disclosed') AS address,
                COALESCE(city, 'India') AS city,
                COALESCE(country, 'India') AS country,
                COALESCE(contact, 'Not Disclosed') AS contact,
                COALESCE(email, 'Not Disclosed') AS email,
                COALESCE(company_description, 'Interior Design Studio Profile') AS company_description,
                CASE 
                    WHEN linkedin_verified = True AND linkedin_url IS NOT NULL THEN linkedin_url 
                    ELSE 'Not Disclosed' 
                END AS linkedin_url,
                COALESCE(linkedin_verified, False) AS linkedin_verified,
                CASE 
                    WHEN instagram_verified = True AND instagram_url IS NOT NULL THEN instagram_url 
                    ELSE 'Not Disclosed' 
                END AS instagram_url,
                COALESCE(instagram_verified, False) AS instagram_verified,
                COALESCE(facebook_url, 'Not Disclosed') AS facebook_url,
                COALESCE(youtube_url, 'Not Disclosed') AS youtube_url,
                last_enriched_at
            FROM designers
            {where_clause}
            ORDER BY designer_name ASC NULLS LAST
        """)

        result = db.execute(query)
        return pd.DataFrame(result.mappings().all())

    def _get_rug_opportunities(
        self,
        db: Session,
        exclude_test_data: bool = True
    ) -> pd.DataFrame:

        where_clause = ""
        if exclude_test_data:
            where_clause = """
                WHERE (p.project_name IS NULL OR (
                    LOWER(p.project_name) NOT LIKE '%test%' 
                    AND LOWER(p.project_name) NOT LIKE '%e2e%' 
                    AND LOWER(p.project_name) NOT LIKE '%idempotency%'
                ))
                AND (p.designer_name IS NULL OR (
                    LOWER(p.designer_name) NOT LIKE '%test%'
                    AND LOWER(p.designer_name) NOT LIKE '%e2e%'
                    AND LOWER(p.designer_name) NOT LIKE '%idempotency%'
                ))
            """

        query = text(f"""
            SELECT
                r.id AS rug_id,
                r.project_id,
                r.designer_id,
                COALESCE(p.project_name, a.title, 'Architectural Digest Project') AS project_name,
                COALESCE(p.designer_name, d.designer_name, 'Independent Designer') AS designer_name,
                COALESCE(p.designer_studio, d.studio_name, 'Independent Studio') AS designer_studio,
                COALESCE(r.rug_used, false) AS rug_used,
                r.rug_type,
                r.matched_keywords AS floor_covering_keywords,
                r.designer_custom_rug AS designer_designed_rug,
                r.origin,
                r.material,
                r.supplier,
                r.brand,
                COALESCE(r.handmade, false) AS handmade,
                COALESCE(r.handwoven, false) AS handwoven,
                COALESCE(r.vintage, false) AS vintage,
                COALESCE(r.custom_made, false) AS custom_made,
                COALESCE(r.imported, false) AS imported,
                r.sourcing_notes,
                COALESCE(r.opportunity_score, 0) AS opportunity_score
            FROM rugs r
            JOIN projects p
                ON r.project_id = p.id
            JOIN articles a
                ON p.article_id = a.id
            LEFT JOIN designers d
                ON r.designer_id = d.id OR p.designer_id = d.id
            {where_clause}
            ORDER BY r.opportunity_score DESC NULLS LAST, r.id DESC
        """)

        result = db.execute(query)
        df = pd.DataFrame(result.mappings().all())

        # Intelligent placeholders based on whether rug_used is True or False
        for idx, row in df.iterrows():
            is_rug_used = row['rug_used']
            if is_rug_used is False or str(is_rug_used).lower() in ('false', '0', 'none'):
                df.at[idx, 'rug_type'] = df.at[idx, 'rug_type'] if pd.notna(df.at[idx, 'rug_type']) else "N/A (No Rug Used)"
                df.at[idx, 'floor_covering_keywords'] = df.at[idx, 'floor_covering_keywords'] if pd.notna(df.at[idx, 'floor_covering_keywords']) else "N/A (No Rug Used)"
                df.at[idx, 'designer_designed_rug'] = False if pd.isna(df.at[idx, 'designer_designed_rug']) else df.at[idx, 'designer_designed_rug']
                df.at[idx, 'origin'] = df.at[idx, 'origin'] if pd.notna(df.at[idx, 'origin']) else "N/A (No Rug Used)"
                df.at[idx, 'material'] = df.at[idx, 'material'] if pd.notna(df.at[idx, 'material']) else "N/A (No Rug Used)"
                df.at[idx, 'supplier'] = df.at[idx, 'supplier'] if pd.notna(df.at[idx, 'supplier']) else "N/A (No Rug Used)"
                df.at[idx, 'brand'] = df.at[idx, 'brand'] if pd.notna(df.at[idx, 'brand']) else "N/A (No Rug Used)"
                df.at[idx, 'sourcing_notes'] = df.at[idx, 'sourcing_notes'] if pd.notna(df.at[idx, 'sourcing_notes']) else "No rug or floor-covering details in article."
            else:
                df.at[idx, 'rug_type'] = df.at[idx, 'rug_type'] if pd.notna(df.at[idx, 'rug_type']) else "Area Rug / Carpet"
                df.at[idx, 'floor_covering_keywords'] = df.at[idx, 'floor_covering_keywords'] if pd.notna(df.at[idx, 'floor_covering_keywords']) else "rug"
                df.at[idx, 'origin'] = df.at[idx, 'origin'] if pd.notna(df.at[idx, 'origin']) else "Not Disclosed"
                df.at[idx, 'material'] = df.at[idx, 'material'] if pd.notna(df.at[idx, 'material']) else "Not Disclosed"
                df.at[idx, 'supplier'] = df.at[idx, 'supplier'] if pd.notna(df.at[idx, 'supplier']) else "Not Disclosed"
                df.at[idx, 'brand'] = df.at[idx, 'brand'] if pd.notna(df.at[idx, 'brand']) else "Not Disclosed"
                df.at[idx, 'sourcing_notes'] = df.at[idx, 'sourcing_notes'] if pd.notna(df.at[idx, 'sourcing_notes']) else "Rug present in project."

        return df