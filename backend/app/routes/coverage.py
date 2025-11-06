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


# ✅ Database Dependency
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

    # ✅ Build cache key (prevents recalculating same walls)
    key = (
        payload.wall_width,
        payload.wall_height,
        tuple((o.x, o.y, o.width, o.height) for o in payload.obstacles),
        payload.step,
    )

    cached = cache.cache.get(key)
    if cached:
        logger.info("♻️ Returning cached coverage result")
        return cached

    # ✅ Convert obstacle list
    obstacles = [
        {"x": o.x, "y": o.y, "width": o.width, "height": o.height}
        for o in payload.obstacles
    ]

    try:
        # ✅ Generate coverage path
        result = generate_coverage_path(
            payload.wall_width, payload.wall_height, obstacles, payload.step
        )

        # Handle both return types (dict or list)
        if isinstance(result, dict) and "points" in result:
            plan_id = result.get("plan_id") or str(uuid4())
            points = result["points"]
        else:
            plan_id = str(uuid4())
            points = result

        # ✅ Validate
        if not points or not isinstance(points, list):
            raise HTTPException(status_code=400, detail="No valid path generated")

        # ✅ Save all points to DB in bulk (single transaction)
        insert_status = crud.create_trajectories(db, plan_id, points)
        if insert_status.get("status") != "success":
            raise HTTPException(status_code=500, detail=insert_status.get("message"))

        # ✅ Build and cache response
        response = {"plan_id": plan_id, "points": points}
        cache.cache.set(key, response, ttl_seconds=60.0)

        logger.info(f"✅ Plan {plan_id} created with {len(points)} points")
        return response

    except Exception as e:
        db.rollback()
        logger.error(f"🔥 Error creating coverage plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
