from fastapi import APIRouter
from backend.app.schemas.common import HealthResponse
from backend.app.config import settings
from backend.app.ml.predictor import get_predictor

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    """
    Health check endpoint returning system status and ML model state.
    """
    predictor = get_predictor()
    return HealthResponse(
        status="ok",
        service="TruthLens API",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        ml_model_loaded=predictor.is_loaded,
        research_available=True,
        news_available=True
    )
