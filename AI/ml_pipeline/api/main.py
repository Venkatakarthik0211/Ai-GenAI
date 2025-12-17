"""FastAPI application for ML Pipeline."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import mlflow
from mlflow.tracking import MlflowClient

from api.routers import pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cleanup_orphaned_mlflow_runs():
    """
    Cleanup MLflow runs that were left in RUNNING state from previous app instances.

    This happens when the app is stopped/restarted while runs are in progress.
    We mark these runs as FAILED with an appropriate message.
    """
    try:
        logger.info("=" * 80)
        logger.info("STARTUP: Checking for orphaned MLflow runs...")
        logger.info("=" * 80)

        client = MlflowClient()
        experiments = client.search_experiments()

        orphaned_count = 0
        for exp in experiments:
            if exp.lifecycle_stage == "active":
                # Find all RUNNING runs in this experiment
                running_runs = client.search_runs(
                    experiment_ids=[exp.experiment_id],
                    filter_string="status = 'RUNNING'",
                    max_results=1000
                )

                for run in running_runs:
                    try:
                        # Mark as FAILED with descriptive message
                        client.set_terminated(
                            run.info.run_id,
                            status="FAILED",
                            end_time=int(datetime.now().timestamp() * 1000)
                        )

                        # Add a tag explaining what happened
                        client.set_tag(
                            run.info.run_id,
                            "termination_reason",
                            "Application restart - run was orphaned"
                        )

                        orphaned_count += 1
                        logger.info(
                            f"  ✓ Marked orphaned run as FAILED: {run.info.run_id} "
                            f"(experiment: {exp.name})"
                        )
                    except Exception as e:
                        logger.error(f"  ✗ Failed to terminate run {run.info.run_id}: {e}")

        if orphaned_count > 0:
            logger.info(f"✓ Cleaned up {orphaned_count} orphaned MLflow run(s)")
        else:
            logger.info("✓ No orphaned MLflow runs found")

        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error during orphaned run cleanup: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown tasks."""
    # Startup
    logger.info("Starting ML Pipeline API...")
    cleanup_orphaned_mlflow_runs()
    logger.info("ML Pipeline API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down ML Pipeline API...")


# Create FastAPI app with lifespan handler
app = FastAPI(
    title="ML Pipeline API",
    description="FastAPI backend for Enhanced ML Pipeline with LangGraph and MLflow",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ML Pipeline API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
