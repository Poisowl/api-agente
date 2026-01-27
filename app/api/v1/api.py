from app.api.v1.process import router as process_router
from app.config.logging import logger
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(process_router, prefix="/agent", tags=["agent"])


@api_router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Health status information.
    """
    logger.info("health_check_called")
    return {"status": "healthy", "version": "1.0.0"}
