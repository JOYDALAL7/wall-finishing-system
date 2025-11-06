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
    Generates a new coverage plan, stores trajectories in DB,
    and returns plan_id + points (normalized).
    """

    # ✅ Create unique cache key
    key = (
        payload.wall_width,
        payload.wall_height,
        tuple((o.x, o.y, o.width, o.height) for o in payload.obstacles),
        payload.step,
    )

    # ✅ Use cached result if exists
    cached = cache.cache.get(key)
    if cached:
        logger.info("♻️ Returning cached coverage result")
        return cached

    # ✅ Build obstacle list
    obstacles = [
        {"x": o.x, "y": o.y, "width": o.width, "height": o.height}
        for o in payload.obstacles
    ]

    try:
        # ✅ Generate coverage path
        raw_result = generate_coverage_path(
            payload.wall_width, payload.wall_height, obstacles, payload.step
        )

        # Normalize response structure
        if isinstance(raw_result, dict) and "points" in raw_result:
            plan_id = raw_result.get("plan_id") or str(uuid4())
            points = raw_result["points"]
        elif isinstance(raw_result, list):
            plan_id = str(uuid4())
            points = raw_result
        else:
            raise HTTPException(status_code=500, detail="Invalid response from path generator")

        # ✅ Ensure all points are valid
        clean_points = []
        for p in points:
            if not isinstance(p, dict):
                continue
            x = float(p.get("x", 0))
            y = float(p.get("y", 0))
            ts = p.get("timestamp", datetime.utcnow().timestamp())
            if isinstance(ts, datetime):
                ts = ts.timestamp()
            clean_points.append({"x": x, "y": y, "timestamp": float(ts)})

        if not clean_points:
            logger.warning("⚠️ No valid points generated for wall plan.")
            raise HTTPException(status_code=400, detail="No valid coverage path generated.")

        # ✅ Store trajectories in DB
        insert_status = crud.create_trajectories(db, plan_id, clean_points)
        if insert_status.get("status") != "success":
            raise HTTPException(status_code=500, detail=insert_status.get("message"))

        # ✅ Build final response
        response = {"plan_id": plan_id, "points": clean_points}
        cache.cache.set(key, response, ttl_seconds=60.0)

        logger.info(f"✅ Coverage plan {plan_id} created with {len(clean_points)} points.")
        return response

    except Exception as e:
        db.rollback()
        logger.error(f"🔥 Error in plan_coverage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {e}")
