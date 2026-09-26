import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.storage.database import SessionLocal
from app.storage.models.designer import DesignerDB
from app.utils.url_validator import validate_social_url


def scrub_database(db: Session, check_live: bool = False) -> dict:
    designers = db.query(DesignerDB).all()

    stats = {
        "total_designers": len(designers),
        "linkedin": {
            "initial_urls": 0,
            "verified": 0,
            "blocked_or_unverified": 0,
            "rejected_invalid": 0,
            "rejected_identity_mismatch": 0
        },
        "instagram": {
            "initial_urls": 0,
            "verified": 0,
            "blocked_or_unverified": 0,
            "rejected_invalid": 0,
            "rejected_identity_mismatch": 0
        },
        "rejected_urls": []
    }

    for d in designers:
        designer_name = d.designer_name or ""
        studio_name = d.studio_name or ""

        # Validate LinkedIn URL
        if d.linkedin_url:
            stats["linkedin"]["initial_urls"] += 1
            val_li = validate_social_url(
                d.linkedin_url,
                designer_name=designer_name,
                studio_name=studio_name,
                check_live=check_live,
                platform_target="linkedin"
            )

            if val_li.verification_status == "VERIFIED":
                d.linkedin_url = val_li.normalized_url or d.linkedin_url
                d.linkedin_verified = True
                d.linkedin_confidence = val_li.confidence
                stats["linkedin"]["verified"] += 1
            elif val_li.verification_status == "BLOCKED_OR_UNVERIFIED":
                d.linkedin_url = val_li.normalized_url or d.linkedin_url
                d.linkedin_verified = False
                d.linkedin_confidence = val_li.confidence
                stats["linkedin"]["blocked_or_unverified"] += 1
            else:
                stats["rejected_urls"].append({
                    "designer_id": d.id,
                    "designer_name": designer_name,
                    "studio_name": studio_name,
                    "platform": "linkedin",
                    "original_url": d.linkedin_url,
                    "reason": val_li.rejection_reason,
                    "status": val_li.verification_status
                })
                if val_li.verification_status == "IDENTITY_MISMATCH":
                    stats["linkedin"]["rejected_identity_mismatch"] += 1
                else:
                    stats["linkedin"]["rejected_invalid"] += 1

                d.linkedin_url = None
                d.linkedin_verified = False
                d.linkedin_confidence = 0.0

        else:
            d.linkedin_verified = False
            d.linkedin_confidence = 0.0

        # Validate Instagram URL
        if d.instagram_url:
            stats["instagram"]["initial_urls"] += 1
            val_ig = validate_social_url(
                d.instagram_url,
                designer_name=designer_name,
                studio_name=studio_name,
                check_live=check_live,
                platform_target="instagram"
            )

            if val_ig.verification_status == "VERIFIED":
                d.instagram_url = val_ig.normalized_url or d.instagram_url
                d.instagram_verified = True
                d.instagram_confidence = val_ig.confidence
                stats["instagram"]["verified"] += 1
            elif val_ig.verification_status == "BLOCKED_OR_UNVERIFIED":
                d.instagram_url = val_ig.normalized_url or d.instagram_url
                d.instagram_verified = False
                d.instagram_confidence = val_ig.confidence
                stats["instagram"]["blocked_or_unverified"] += 1
            else:
                stats["rejected_urls"].append({
                    "designer_id": d.id,
                    "designer_name": designer_name,
                    "studio_name": studio_name,
                    "platform": "instagram",
                    "original_url": d.instagram_url,
                    "reason": val_ig.rejection_reason,
                    "status": val_ig.verification_status
                })
                if val_ig.verification_status == "IDENTITY_MISMATCH":
                    stats["instagram"]["rejected_identity_mismatch"] += 1
                else:
                    stats["instagram"]["rejected_invalid"] += 1

                d.instagram_url = None
                d.instagram_verified = False
                d.instagram_confidence = 0.0

        else:
            d.instagram_verified = False
            d.instagram_confidence = 0.0

    db.commit()
    return stats


if __name__ == "__main__":
    db = SessionLocal()
    try:
        results = scrub_database(db, check_live=False)
        print("\n=== SOCIAL URL DATABASE SCRUBBING REPORT ===")
        print(f"Total Designers Evaluated: {results['total_designers']}")
        print(f"LinkedIn URLs Evaluated: {results['linkedin']['initial_urls']}")
        print(f"  - Verified Profile URLs: {results['linkedin']['verified']}")
        print(f"  - Blocked/Unverified: {results['linkedin']['blocked_or_unverified']}")
        print(f"  - Rejected Invalid Paths/Legal: {results['linkedin']['rejected_invalid']}")
        print(f"  - Rejected Identity Mismatches: {results['linkedin']['rejected_identity_mismatch']}")
        print(f"Instagram URLs Evaluated: {results['instagram']['initial_urls']}")
        print(f"  - Verified Profile URLs: {results['instagram']['verified']}")
        print(f"  - Blocked/Unverified: {results['instagram']['blocked_or_unverified']}")
        print(f"  - Rejected Invalid Paths/Home: {results['instagram']['rejected_invalid']}")
        print(f"  - Rejected Identity Mismatches: {results['instagram']['rejected_identity_mismatch']}")
        print(f"\nTotal Rejected Bad URLs: {len(results['rejected_urls'])}\n")

        for r in results['rejected_urls']:
            print(f"[{r['platform'].upper()}] ID {r['designer_id']} ({r['designer_name']}): {r['original_url']} -> REJECTED: {r['reason']}")

    finally:
        db.close()
