# backend/app/routes/coverage.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app import schemas, crud
from app.database import SessionLocal
from app.utils.coverage_planner import generate_coverage_path
from app.utils import cache
from app.utils.logging import logger

router = APIRouter(tags=["Coverage"])


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

    # ✅ Generate coverage path (returns dict with plan_id + points)
    result = generate_coverage_path(
        payload.wall_width, payload.wall_height, obstacles, payload.step
    )

    plan_id = result["plan_id"]
    points = result["points"]

    # ✅ Store points in DB safely
    crud.create_trajectories(db, plan_id, points)

    # ✅ Cache + Return response
    response = {"plan_id": plan_id, "points": points}
    cache.cache.set(key, response, ttl_seconds=60.0)

    logger.info(f"Created plan {plan_id} with {len(points)} points")
    return response
