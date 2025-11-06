from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud
from app.utils.logging import logger
import asyncio

router = APIRouter(tags=["Player"])

ALLOWED_ORIGINS = {
    "https://wall-finishing-system.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}

@router.websocket("/ws/play/{plan_id}")
async def websocket_play(websocket: WebSocket, plan_id: str):
    """
    Streams trajectory points for a given plan_id over WebSocket.
    Compatible with Vercel frontend + Render backend.
    """
    origin = websocket.headers.get("origin")
    logger.info(f"🌐 WebSocket request from: {origin}")

    # ✅ Allow only trusted origins
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008)
        logger.warning(f"❌ WebSocket rejected from invalid origin: {origin}")
        return

    await websocket.accept()
    db: Session = SessionLocal()

    try:
        rows = crud.get_trajectories_by_plan(db, plan_id)

        if not rows:
            await websocket.send_json({"error": "plan_not_found"})
            await websocket.close()
            logger.warning(f"⚠️ Plan '{plan_id}' not found.")
            return

        total = len(rows)
        logger.info(f"🎬 Streaming {total} points for plan_id={plan_id}")

        for i, row in enumerate(rows):
            ts = (
                row.timestamp.timestamp()
                if hasattr(row.timestamp, "timestamp")
                else row.timestamp
            )
            await websocket.send_json({
                "x": float(row.x),
                "y": float(row.y),
                "index": i,
                "total": total,
                "timestamp": ts,
            })
            await asyncio.sleep(0.05)

        logger.info(f"✅ Completed playback for plan {plan_id}")
        await websocket.close()

    except WebSocketDisconnect:
        logger.info(f"🔌 Client disconnected from /ws/play/{plan_id}")
    except Exception as e:
        logger.error(f"🔥 WebSocket error for {plan_id}: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
        await websocket.close()
    finally:
        db.close()
