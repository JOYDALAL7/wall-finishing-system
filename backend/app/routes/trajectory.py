from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.utils.logging import logger
import asyncio
from datetime import datetime

router = APIRouter(tags=["Trajectory"])

# ✅ GET all trajectories (base route)
@router.get("/", response_model=list[schemas.TrajectoryResponse])
def get_all(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    rows = crud.get_recent_trajectories(db, limit=limit)
    if not rows:
        return []
    return rows

# ✅ GET recent trajectories
@router.get("/recent", response_model=list[schemas.TrajectoryResponse])
def get_recent(limit: int = Query(50, ge=1, le=1000), db: Session = Depends(get_db)):
    rows = crud.get_recent_trajectories(db, limit=limit)
    if not rows:
        return []
    return rows

# ✅ GET trajectories by plan ID
@router.get("/{plan_id}", response_model=list[schemas.TrajectoryResponse])
def get_by_plan(plan_id: str, db: Session = Depends(get_db)):
    rows = crud.get_trajectories_by_plan(db, plan_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Plan not found")
    return rows

# ✅ WebSocket endpoint for live playback (backup)
@router.websocket("/ws/play/{plan_id}")
async def play_trajectory(websocket: WebSocket, plan_id: str, db: Session = Depends(get_db)):
    """
    Streams stored trajectory points one-by-one over WebSocket.
    Sends {"x":..., "y":..., "index":..., "total":...} every 0.05s.
    Gracefully handles disconnection.
    """
    await websocket.accept()
    try:
        rows = crud.get_trajectories_by_plan(db, plan_id)
        if not rows:
            await websocket.send_json({"error": "plan_not_found"})
            await websocket.close()
            return

        total = len(rows)
        logger.info(f"🎬 Streaming {total} points for plan_id={plan_id}")

        for idx, row in enumerate(rows):
            payload = {
                "x": row.x,
                "y": row.y,
                "index": idx,
                "total": total,
                "timestamp": (
                    row.timestamp.timestamp() if isinstance(row.timestamp, datetime) else row.timestamp
                ),
            }
            await websocket.send_json(payload)
            await asyncio.sleep(0.05)

        logger.info(f"✅ Completed playback for {plan_id}")
        await websocket.close()

    except WebSocketDisconnect:
        logger.info(f"🔌 Client disconnected from /ws/play/{plan_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for {plan_id}: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
        await websocket.close()
