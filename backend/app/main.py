# backend/app/main.py

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware  # ✅ use FastAPI’s version for full OPTIONS support
import time
from app.database import Base, engine
from app.routes import coverage, trajectory, player
from app.utils.logging import logger

# ✅ Initialize FastAPI app
app = FastAPI(title="Wall Finishing Planner API")

# ✅ Create all database tables at startup
Base.metadata.create_all(bind=engine)

# ✅ Define allowed frontend origins (local + deployed)
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://wall-finishing-system.vercel.app",
    "https://www.wall-finishing-system.vercel.app",
    "https://wall-finishing-system.onrender.com",
]

# ✅ CORS middleware (put BEFORE any other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE, OPTIONS etc.
    allow_headers=["*"],  # Allow all headers (Content-Type, Authorization, etc.)
)

# ✅ Logging middleware (added AFTER CORS)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"🔥 Exception while processing {request.url.path}: {e}")
        raise
    duration = round(time.time() - start_time, 4)
    response.headers["X-Response-Time"] = str(duration)
    logger.info(f"{request.method} {request.url.path} - {duration}s - {response.status_code}")
    return response

# ✅ Register REST API routers
app.include_router(coverage.router, prefix="/api/coverage", tags=["Coverage"])
app.include_router(trajectory.router, prefix="/api/trajectory", tags=["Trajectory"])
app.include_router(player.router, prefix="/api/player", tags=["Player"])

# ✅ Health check endpoint
@app.get("/")
async def root():
    return {"message": "✅ Backend API is running successfully!"}

# ✅ WebSocket Test Route (optional for Render/Vercel check)
@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """
    Verifies if Render allows WebSocket upgrade from your frontend.
    """
    origin = websocket.headers.get("origin", "")
    logger.info(f"🌐 WebSocket request from: {origin}")

    # ✅ Allow requests from trusted frontend domains
    trusted_domains = [
        "vercel.app",
        "localhost",
        "127.0.0.1",
        "onrender.com",
    ]

    if not any(domain in origin for domain in trusted_domains):
        logger.warning(f"❌ WebSocket rejected from: {origin}")
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await websocket.send_json({
        "status": "connected ✅",
        "origin": origin,
    })
    logger.info(f"✅ WebSocket connection established from {origin}")
    await websocket.close()
