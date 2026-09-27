import pytest
from pathlib import Path
from app.ml.predictor import NewsPredictor
from app.ml.dataset import load_news_dataset


def test_predictor_unloaded_fallback():
    predictor = NewsPredictor()
    # If no model weights exist yet
    if not predictor.is_loaded:
        res = predictor.predict("Any sample news headline")
        assert res["is_loaded"] is False
        assert res["prediction"] is None
        assert "not trained yet" in res["message"].lower()


def test_dataset_loader_missing_file():
    with pytest.raises(FileNotFoundError):
        load_news_dataset(Path("non_existent_dataset_file.csv"))
