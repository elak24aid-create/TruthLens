import os
import joblib
from typing import Dict, Any, List, Optional
import numpy as np

from app.config import settings


class NewsPredictor:
    """
    Inference service for fake news detection using trained TF-IDF + Logistic Regression.
    Handles unloaded state gracefully without manufacturing fake statistics.
    """

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self) -> bool:
        if os.path.exists(settings.ML_MODEL_PATH) and os.path.exists(settings.ML_VECTORIZER_PATH):
            try:
                self.model = joblib.load(settings.ML_MODEL_PATH)
                self.vectorizer = joblib.load(settings.ML_VECTORIZER_PATH)
                self.is_loaded = True
                return True
            except Exception as e:
                print(f"[!] Warning: Failed to load saved ML model: {e}")
                self.is_loaded = False
                return False
        self.is_loaded = False
        return False

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Runs ML prediction if model is trained.
        Returns probability distribution and significant influential terms.
        """
        if not self.is_loaded:
            # Try reloading in case it was just trained
            if not self._load_model():
                return {
                    "is_loaded": False,
                    "prediction": None,
                    "probability_misleading": None,
                    "probability_genuine": None,
                    "confidence": None,
                    "influential_terms": [],
                    "message": "ML model not trained yet. Requires dataset at backend/data/news_dataset.csv",
                }

        # Transform text
        vec = self.vectorizer.transform([text])
        probabilities = self.model.predict_proba(vec)[0]  # [prob_genuine(0), prob_misleading(1)]
        prob_genuine = float(probabilities[0])
        prob_misleading = float(probabilities[1])

        # Prediction decision based on 0.5 threshold
        if prob_misleading >= 0.5:
            verdict = "Likely Misleading"
            confidence = int(round(prob_misleading * 100))
        else:
            verdict = "Likely Genuine"
            confidence = int(round(prob_genuine * 100))

        # Extract top influential tokens for explainability
        influential_terms = self._get_influential_terms(vec)

        return {
            "is_loaded": True,
            "prediction": verdict,
            "probability_misleading": round(prob_misleading, 4),
            "probability_genuine": round(prob_genuine, 4),
            "confidence": confidence,
            "influential_terms": influential_terms,
            "message": "Model inference computed successfully.",
        }

    def _get_influential_terms(self, vec, top_n: int = 5) -> List[str]:
        """
        Identifies top words/phrases present in input text that contributed most
        strongly to the logistic regression decision.
        """
        try:
            feature_names = self.vectorizer.get_feature_names_out()
            feature_indices = vec.nonzero()[1]
            if len(feature_indices) == 0:
                return []

            coefficients = self.model.coef_[0]
            # Pair feature with its model coefficient
            scored_terms = [
                (feature_names[idx], coefficients[idx])
                for idx in feature_indices
            ]
            # Sort by absolute magnitude of coefficient
            scored_terms.sort(key=lambda x: abs(x[1]), reverse=True)
            return [term for term, _ in scored_terms[:top_n]]
        except Exception:
            return []


# Global singleton instance
_predictor_instance: Optional[NewsPredictor] = None


def get_predictor() -> NewsPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = NewsPredictor()
    return _predictor_instance
