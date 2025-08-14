# file: app/main.py
# The updated main application entry point.

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Corrected imports for the new structure
from app.core.database import create_db_and_tables
from app.api import endpoints

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    title="Thought Experiment Simulator (TES)",
    description="Backend service for generating and running thought experiments.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(endpoints.router, prefix="/api")


@app.get("/")
async def read_root():
    """A simple root endpoint to confirm the server is running."""
    return {"message": "Welcome to the TES Backend!"}