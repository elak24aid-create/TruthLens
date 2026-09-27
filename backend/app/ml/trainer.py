import os
import json
from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.config import settings
from app.ml.dataset import load_news_dataset
from app.ml.evaluation import compute_metrics


def train_model(dataset_path: Path = None) -> dict:
    """
    Trains the real TF-IDF + Logistic Regression fake news detector.
    Does not invent fake data. Requires real dataset CSV.
    """
    path = dataset_path or settings.DATASET_PATH

    print(f"[*] Checking for dataset at: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"\n[ERROR] Dataset not found at: {path}\n"
            "To train the model with real data, please provide a CSV file with news articles and labels.\n"
            "Recommended benchmark datasets:\n"
            "  1. WELFake dataset (Kaggle)\n"
            "  2. ISOT Fake News Dataset\n"
            "  3. LIAR dataset\n"
            "Place the CSV at: backend/data/news_dataset.csv\n"
            "Expected columns: 'text' (or 'title'+'text') and 'label' (0 = Genuine, 1 = Misleading)."
        )

    print("[*] Loading dataset...")
    X, y = load_news_dataset(path)
    print(f"[*] Loaded {len(X)} valid samples. Label distribution: Genuine={sum(y==0)}, Misleading={sum(y==1)}")

    # Split train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[*] Train set: {len(X_train)} samples | Test set: {len(X_test)} samples")

    # Vectorization
    print("[*] Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        stop_words="english",
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Model Training
    print("[*] Training Logistic Regression Classifier...")
    model = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    model.fit(X_train_vec, y_train)

    # Evaluation
    print("[*] Evaluating on test set...")
    y_pred = model.predict(X_test_vec)
    metrics = compute_metrics(y_test.to_numpy(), y_pred)

    print("\n" + "=" * 45)
    print("      REAL MODEL EVALUATION RESULTS")
    print("=" * 45)
    print(f"Accuracy:         {metrics['accuracy'] * 100:.2f}%")
    print(f"Precision:        {metrics['precision'] * 100:.2f}%")
    print(f"Recall:           {metrics['recall'] * 100:.2f}%")
    print(f"F1-Score:         {metrics['f1_score'] * 100:.2f}%")
    print(f"Confusion Matrix: {metrics['confusion_matrix']}")
    print(f"Test Samples:     {metrics['sample_size']}")
    print("=" * 45 + "\n")

    # Save artifacts
    save_dir = settings.ML_MODEL_PATH.parent
    save_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, settings.ML_MODEL_PATH)
    joblib.dump(vectorizer, settings.ML_VECTORIZER_PATH)
    with open(settings.ML_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[+] Model saved to: {settings.ML_MODEL_PATH}")
    print(f"[+] Vectorizer saved to: {settings.ML_VECTORIZER_PATH}")
    print(f"[+] Metrics saved to: {settings.ML_METRICS_PATH}")

    return metrics


if __name__ == "__main__":
    try:
        train_model()
    except FileNotFoundError as e:
        print(e)
