from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud
from app.utils.logging import logger
import asyncio

router = APIRouter(tags=["Player"])


@router.websocket("/ws/play/{plan_id}")
async def websocket_play(websocket: WebSocket, plan_id: str):
    """
    WebSocket endpoint to stream trajectory points for a given plan_id.
    Handles both ORM and dict-style results safely.
    """
    await websocket.accept()
    db: Session = SessionLocal()

    try:
        rows = crud.get_trajectories_by_plan(db, plan_id)

        if not rows:
            await websocket.send_json({"error": "plan_not_found"})
            await websocket.close()
            logger.warning(f"WebSocket: Plan '{plan_id}' not found.")
            return

        total = len(rows)
        logger.info(f"🎬 WebSocket playback started for plan {plan_id} ({total} points)")

        for i, row in enumerate(rows):
            # ✅ Handle dict or ORM result safely
            if isinstance(row, dict):
                ts = row.get("timestamp")
                x = row.get("x")
                y = row.get("y")
            else:  # Fallback (if ORM object)
                ts = (
                    row.timestamp.timestamp()
                    if hasattr(row.timestamp, "timestamp")
                    else row.timestamp
                )
                x = row.x
                y = row.y

            await websocket.send_json({
                "x": float(x),
                "y": float(y),
                "index": i,
                "total": total,
                "timestamp": ts,
            })
            await asyncio.sleep(0.05)

        await websocket.close()
        logger.info(f"✅ Playback completed for plan {plan_id}")

    except WebSocketDisconnect:
        logger.info(f"❌ WebSocket disconnected for plan {plan_id}")
    except Exception as e:
        logger.error(f"🔥 WebSocket error for plan {plan_id}: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
        await websocket.close()
    finally:
        db.close()
