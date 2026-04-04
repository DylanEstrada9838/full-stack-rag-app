"""
main.py — FastAPI application entry point.

This file is intentionally minimal. Its only jobs are:
  1. Create the FastAPI app instance.
  2. Register CORS middleware.
  3. Load / unload the RAG pipeline on startup / shutdown (via lifespan).
  4. Register the API routes.

All other concerns live in dedicated modules:
  config.py   — paths and constants
  state.py    — shared ML objects (retriever, chain)
  pipeline.py — RAG initialisation logic
  models.py   — Pydantic request / response schemas
  routes.py   — endpoint definitions
  logger.py   — terminal logging helpers

Run with:
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from pipeline import load_pipeline, unload_pipeline
from routes import router

# Load environment variables (HF_TOKEN, etc.) from .env
load_dotenv()


# ---------------------------------------------------------------------------
# Lifespan: startup ➜ load pipeline | shutdown ➜ unload pipeline
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting RAG backend...")
    load_pipeline()
    yield
    unload_pipeline()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="RAG Reglamento Tec API",
    description="Q&A assistant for the Reglamento General de Estudiantes",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
