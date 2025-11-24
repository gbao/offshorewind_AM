"""
Offshore Wind Operational Performance Hub - FastAPI Application

Main entry point for the backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import engine, Base
from app.api.routes import router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup on shutdown (if needed)


app = FastAPI(
    title=settings.app_name,
    description="""
    ## Offshore Wind Operational Performance Hub

    A comprehensive monitoring and reporting platform for operational offshore wind projects.

    ### Features:
    - **Financial Statements**: Track P&L, Balance Sheet, and Cash Flow
    - **Production Data**: Monitor generation, availability, and capacity factors
    - **Debt Management**: Track loan facilities, movements, and covenants
    - **KPI Analytics**: Calculate EBITDA, DSCR, margins, and more
    - **Portfolio View**: Compare multiple projects

    ### Data Input:
    - Structured forms for manual entry
    - Paste/upload parser for extracting data from documents
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint - API info."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
