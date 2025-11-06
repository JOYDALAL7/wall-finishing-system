from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from datetime import datetime
from app.utils.logging import logger

router = APIRouter(tags=["Trajectory"])

# ✅ GET all trajectories (recent)
@router.get("/")
def get_all(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    rows = crud.get_recent_trajectories(db, limit=limit)
    return rows or []


# ✅ GET recent trajectories
@router.get("/recent")
def get_recent(limit: int = Query(50, ge=1, le=1000), db: Session = Depends(get_db)):
    rows = crud.get_recent_trajectories(db, limit=limit)
    return rows or []


# ✅ GET trajectories by plan_id (frontend simplified response)
@router.get("/{plan_id}")
def get_by_plan(plan_id: str, db: Session = Depends(get_db)):
    """
    Returns simplified trajectory points for a given plan_id
    (x, y, timestamp) only — for frontend visualization.
    Works with both ORM objects and dicts.
    """
    rows = crud.get_trajectories_by_plan(db, plan_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Plan not found")

    formatted = []
    for idx, r in enumerate(rows):
        # ✅ Handle both dict and ORM
        x = r["x"] if isinstance(r, dict) else getattr(r, "x", None)
        y = r["y"] if isinstance(r, dict) else getattr(r, "y", None)
        ts_raw = r["timestamp"] if isinstance(r, dict) else getattr(r, "timestamp", None)

        ts_value = None
        try:
            if hasattr(ts_raw, "timestamp"):  # datetime
                ts_value = ts_raw.timestamp()
            elif isinstance(ts_raw, (int, float)):
                ts_value = float(ts_raw)
            elif isinstance(ts_raw, str):
                try:
                    ts_value = datetime.fromisoformat(ts_raw).timestamp()
                except Exception:
                    ts_value = float(idx)
            elif isinstance(ts_raw, dict):
                inner = ts_raw.get("value") or ts_raw.get("timestamp")
                if isinstance(inner, (int, float)):
                    ts_value = float(inner)
                elif isinstance(inner, str):
                    try:
                        ts_value = datetime.fromisoformat(inner).timestamp()
                    except Exception:
                        ts_value = float(idx)
            else:
                ts_value = float(idx)
        except Exception as e:
            logger.warning(f"⚠️ Invalid timestamp for point {idx}: {e}")
            ts_value = float(idx)

        if x is None or y is None:
            continue

        formatted.append({
            "x": float(x),
            "y": float(y),
            "timestamp": ts_value,
        })

    logger.info(f"✅ Returned {len(formatted)} simplified points for plan_id={plan_id}")
    return formatted
