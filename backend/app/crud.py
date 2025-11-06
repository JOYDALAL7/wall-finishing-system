from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app import models


def create_trajectories(db: Session, plan_id: str, points: list[dict]):
    """
    Inserts coverage path points into the database safely and reliably.
    Commits once after all inserts and ensures timestamps are consistent.
    """

    if not isinstance(points, list) or len(points) == 0:
        return {"status": "error", "message": "Invalid points data"}

    clean_points = [
        p for p in points
        if isinstance(p, dict) and "x" in p and "y" in p
    ]

    if not clean_points:
        return {"status": "error", "message": "No valid points to insert"}

    objs = []
    for p in clean_points:
        ts = p.get("timestamp")
        if isinstance(ts, (int, float)):
            ts = datetime.fromtimestamp(ts)
        elif not isinstance(ts, datetime):
            ts = datetime.utcnow()

        objs.append(
            models.Trajectory(
                plan_id=plan_id,
                x=float(p["x"]),
                y=float(p["y"]),
                timestamp=ts,
                created_at=datetime.utcnow()
            )
        )

    try:
        db.add_all(objs)
        db.flush()   # ✅ ensures objects are actually written before commit
        db.commit()  # ✅ persist changes
        db.refresh(objs[-1])  # ✅ refresh last one to ensure visibility
        return {"status": "success", "count": len(objs)}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


def get_recent_trajectories(db: Session, limit: int = 50):
    """
    Returns the most recent trajectories with float timestamps.
    """
    rows = (
        db.query(models.Trajectory)
        .order_by(desc(models.Trajectory.created_at))
        .limit(limit)
        .all()
    )

    result = []
    for row in rows:
        ts = (
            row.timestamp.timestamp()
            if hasattr(row.timestamp, "timestamp")
            else float(row.timestamp)
        )

        result.append({
            "id": row.id,
            "x": float(row.x),
            "y": float(row.y),
            "timestamp": ts,
            "plan_id": row.plan_id,
            "created_at": row.created_at,
        })
    return result


def get_trajectories_by_plan(db: Session, plan_id: str):
    """Fetch all trajectory points for a given plan."""
    rows = (
        db.query(models.Trajectory)
        .filter(models.Trajectory.plan_id == plan_id)
        .order_by(models.Trajectory.id.asc())
        .all()
    )

    result = []
    for row in rows:
        ts = (
            row.timestamp.timestamp()
            if hasattr(row.timestamp, "timestamp")
            else float(row.timestamp)
        )
        result.append({
            "id": row.id,
            "x": float(row.x),
            "y": float(row.y),
            "timestamp": ts,
            "plan_id": row.plan_id,
            "created_at": row.created_at,
        })
    return result
