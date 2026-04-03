"""
app/main.py
───────────
FastAPI application entry point.

This file:
  1. Creates the FastAPI app
  2. Configures CORS (allows the React frontend to talk to this backend)
  3. Registers all API routers
  4. Sets up startup/shutdown hooks (DB table creation, etc.)
  5. Adds global error handling

HOW TO RUN:
  Development:  uvicorn app.main:app --reload --port 8000
  Production:   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Then visit:  http://localhost:8000/docs  (interactive API documentation)
"""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import create_tables

# Import all routers
from app.api.auth  import router as auth_router
from app.api.scans import router as scans_router

settings = get_settings()

# ── Configure logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if settings.APP_ENV == "production" else logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("rangard")


# ── Create the FastAPI app ────────────────────────────────────────────────────

app = FastAPI(
    title="RANGARD API",
    description=(
        "AI-powered ransomware detection and blockchain-backed file versioning. "
        "Upload files to scan them for ransomware behaviour, quarantine threats, "
        "and anchor clean file hashes to Ethereum for immutable versioning."
    ),
    version="1.0.0",
    docs_url="/docs",     # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",   # ReDoc UI at http://localhost:8000/redoc
)


# ── CORS: allow the React frontend to call this API ───────────────────────────
# In development, React runs on localhost:3000 or :5173 (Vite)
# In production, replace with your real domain

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Register routers ──────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(scans_router)


# ── Startup / Shutdown ────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info(f"  RANGARD API  |  {settings.APP_ENV.upper()}")
    logger.info("=" * 60)

    # Create quarantine directory
    os.makedirs(settings.QUARANTINE_DIR, exist_ok=True)
    logger.info(f"  Quarantine dir:  {settings.QUARANTINE_DIR}")

    # Auto-create DB tables in development
    # In production: use `alembic upgrade head` instead
    if settings.APP_ENV == "development":
        try:
            await create_tables()
            logger.info("  Database tables created/verified")
        except Exception as e:
            logger.error(f"  DB setup failed (is PostgreSQL running?): {e}")
            logger.info("  Tip: run `docker-compose up db` to start PostgreSQL")

    # Log ML model status
    from app.ml.detector import get_detector
    detector = get_detector()
    if detector.model is not None:
        logger.info("  ML model:        LOADED (trained RandomForest)")
    else:
        logger.info("  ML model:        RULE-BASED (train a model for higher accuracy)")

    # Log blockchain status
    from app.blockchain.service import get_blockchain_service
    bc = get_blockchain_service()
    mode = "LIVE" if not bc.demo_mode else "DEMO (no Infura key)"
    logger.info(f"  Blockchain:      {mode}")

    logger.info("  API docs:        http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown():
    logger.info("RANGARD API shutting down...")


# ── Global error handlers ─────────────────────────────────────────────────────

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "path": str(request.url.path)},
    )


@app.exception_handler(500)
async def server_error(request: Request, exc):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error — check server logs"},
    )


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """
    Simple health check for load balancers and uptime monitors.
    Returns 200 if the server is running.
    """
    return {
        "status": "ok",
        "service": "RANGARD API",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "RANGARD API — visit /docs for interactive documentation",
        "docs": "/docs",
        "health": "/health",
    }
