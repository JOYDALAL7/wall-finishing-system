# backend/app/main.py

from fastapi import FastAPI, Request, WebSocket
from starlette.middleware.cors import CORSMiddleware
import time
from app.database import Base, engine
from app.routes import coverage, trajectory, player  # ✅ WebSocket route included
from app.utils.logging import logger

# ✅ Create all database tables
Base.metadata.create_all(bind=engine)

# ✅ Initialize FastAPI app
app = FastAPI(title="Wall Finishing Planner API")

# ✅ CORS setup — allow both localhost and Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://wall-finishing-system.vercel.app",  # ✅ your Vercel frontend
        "https://wall-finishing-system.onrender.com",  # ✅ your backend (self)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Middleware for logging and request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round(time.time() - start_time, 4)
    response.headers["X-Response-Time"] = str(duration)
    logger.info(f"{request.method} {request.url.path} - {duration}s - {response.status_code}")
    return response


# ✅ Register REST + WebSocket routes
app.include_router(coverage.router, prefix="/api/coverage", tags=["Coverage"])
app.include_router(trajectory.router, prefix="/api/trajectory", tags=["Trajectory"])
app.include_router(player.router)  # ✅ No prefix for WebSocket routes


# ✅ Health check
@app.get("/")
async def root():
    return {"message": "Backend API is running successfully!"}


# ✅ Quick WebSocket test endpoint (for Render)
@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """
    Simple WebSocket handshake test.
    Confirms that Render allows WebSocket upgrade from Vercel frontend.
    """
    origin = websocket.headers.get("origin")
    logger.info(f"🌐 WebSocket request from: {origin}")

    # Only allow trusted origins
    if origin not in [
        "https://wall-finishing-system.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]:
        await websocket.close(code=1008)
        logger.warning(f"❌ WebSocket rejected due to invalid origin: {origin}")
        return

    await websocket.accept()
    await websocket.send_json({"status": "connected ✅", "origin": origin})
    logger.info(f"✅ WebSocket connection established from {origin}")
    await websocket.close()
