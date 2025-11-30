import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Request
from time import time

from app.api.individuals import router as individuals_router
from app.api.auth import router as auth_router
from app.api.relationship import router as relation_router
from app.api.tree import router as tree_router
from app.api.graph_admin import router as graph_admin_router
from app.api.graph_tree import router as graph_tree_router


# ------------------------------------
# Configure Logging
# ------------------------------------
LOG_FILE = "logs/app.log"

# Create log directory if not exists
import os
os.makedirs("logs", exist_ok=True)


logger = logging.getLogger("family_tree")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=2_000_000, backupCount=5
)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI(
    title="Family Tree API",
    version="1.0.0"
)

# Log every incoming request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time()
    logger.info(f"Incoming request: {request.method} {request.url}")

    response = await call_next(request)

    duration = time() - start_time
    logger.info(
        f"Completed: {request.method} {request.url} "
        f"Status: {response.status_code} "
        f"Time: {duration:.3f}s"
    )

    return response


# ---------------------------
# Routers
# ---------------------------
app.include_router(individuals_router)
app.include_router(auth_router)
app.include_router(relation_router)
app.include_router(tree_router)
app.include_router(graph_admin_router)
app.include_router(graph_tree_router)

@app.get("/")
def root():
    logger.info("Health check endpoint requested")
    return {"message":"Family Tree API is running 🚀"}
