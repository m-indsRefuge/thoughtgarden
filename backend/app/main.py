# file: app/main.py
# The updated main application entry point with CORS middleware.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Corrected imports for the new structure
from app.core.database import create_db_and_tables
from app.api import endpoints

# Configure logging
# This is a good place to set the default logging level for the application.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tes_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup events: create database tables.
    """
    logger.info("Application starting up...")
    await create_db_and_tables()
    logger.info("Database is ready.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title="Thought Garden",
    description="Backend service for generating and running thought experiments.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Add CORS Middleware ---
# This section allows our frontend (running on localhost:1420) to communicate
# with our backend (running on localhost:8001).
origins = [
    "http://localhost:1420",
    "tauri://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End of CORS Middleware ---


app.include_router(endpoints.router, prefix="/api")


@app.get("/")
async def read_root():
    """A simple root endpoint to confirm the server is running."""
    return {"message": "Welcome to the Thought Garden Backend!"}