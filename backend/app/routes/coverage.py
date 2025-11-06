# backend/app/routes/coverage.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app import schemas, crud
from app.database import SessionLocal
from app.utils.coverage_planner import generate_coverage_path
from app.utils import cache
from app.utils.logging import logger
from datetime import datetime

router = APIRouter(tags=["Coverage"])


# ✅ DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.CoverageResponse)
def plan_coverage(payload: schemas.CoverageRequest, db: Session = Depends(get_db)):
    """
    Generates a new coverage plan with obstacle avoidance,
    stores trajectories in DB, and returns plan_id + points.
    """

    # ✅ Create cache key
    key = (
        payload.wall_width,
        payload.wall_height,
        tuple((o.x, o.y, o.width, o.height) for o in payload.obstacles),
        payload.step,
    )

    # ✅ Use cache if available
    cached = cache.cache.get(key)
    if cached:
        logger.info("Coverage result returned from cache")
        return cached

    # ✅ Build obstacle list
    obstacles = [
        {"x": o.x, "y": o.y, "width": o.width, "height": o.height}
        for o in payload.obstacles
    ]

    # ✅ Generate new coverage plan
    plan_id = str(uuid4())
    points = generate_coverage_path(
        payload.wall_width, payload.wall_height, obstacles, payload.step
    )

    # ✅ Ensure result format
    if not points:
        raise HTTPException(status_code=400, detail="No valid coverage path generated")

    # ✅ Save each trajectory to DB
    try:
        for p in points:
            traj = schemas.TrajectoryCreate(
                x=p["x"],
                y=p["y"],
                timestamp=p["timestamp"],
                plan_id=plan_id,
            )
            crud.create_trajectory(db, traj)

        db.commit()  # ✅ Important: persist all trajectories

        logger.info(f"✅ Created plan {plan_id} with {len(points)} points")

        response = {"plan_id": plan_id, "points": points}
        cache.cache.set(key, response, ttl_seconds=60.0)
        return response

    except Exception as e:
        db.rollback()
        logger.error(f"🔥 Error creating trajectories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
