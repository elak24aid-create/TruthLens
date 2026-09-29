import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    # Security
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    ]
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_truthlens")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "500"))

    # ML Model Paths
    ML_MODEL_PATH: Path = BASE_DIR / os.getenv(
        "ML_MODEL_PATH", "app/ml/saved_models/model.joblib"
    )
    ML_VECTORIZER_PATH: Path = BASE_DIR / os.getenv(
        "ML_VECTORIZER_PATH", "app/ml/saved_models/vectorizer.joblib"
    )
    ML_METRICS_PATH: Path = BASE_DIR / os.getenv(
        "ML_METRICS_PATH", "app/ml/saved_models/metrics.json"
    )

    # Dataset Path
    # Project root (two levels up from this file)
    ROOT_DIR: Path = Path(__file__).resolve().parents[2]
    DATASET_PATH: Path = ROOT_DIR / os.getenv("DATASET_PATH", "data/news_dataset.csv")

    # External APIs (Optional Phase 2)
    GOOGLE_FACT_CHECK_API_KEY: str = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")


settings = Settings()
