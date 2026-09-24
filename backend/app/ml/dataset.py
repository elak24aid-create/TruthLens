import os
from pathlib import Path
from typing import Tuple
import pandas as pd


def load_news_dataset(file_path: Path) -> Tuple[pd.Series, pd.Series]:
    """
    Loads and validates a real news dataset from CSV.
    Detects text and label columns, normalizes binary classification targets.
    
    Expected format:
      CSV file with at least two columns:
      - Text column (e.g. 'text', 'content', 'article', or combined 'title' + 'text')
      - Label column (e.g. 'label', 'target', 'fake', 'class')
        where 0 = Real / Genuine news, 1 = Fake / Misleading news.
        (Also accepts string labels like 'REAL'/'FAKE', 'TRUE'/'FALSE').
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset not found at: {file_path}.\n"
            "Please place a real news dataset CSV (e.g., WELFake, ISOT, or Kaggle Fake News) "
            "at the specified path with columns for text and binary label (0 = genuine, 1 = misleading)."
        )

    df = pd.read_csv(file_path)

    # Detect text column
    text_candidates = ["text", "content", "article", "statement", "news", "body"]
    found_text_col = None
    for col in df.columns:
        if col.lower().strip() in text_candidates:
            found_text_col = col
            break

    # If title exists, combine title and text for richer context
    title_candidates = ["title", "headline"]
    found_title_col = None
    for col in df.columns:
        if col.lower().strip() in title_candidates:
            found_title_col = col
            break

    if not found_text_col and not found_title_col:
        raise ValueError(
            f"Could not identify a text column in CSV with columns: {list(df.columns)}. "
            "Please ensure the CSV has a column named 'text' or 'title'."
        )

    if found_title_col and found_text_col:
        X = df[found_title_col].fillna("").astype(str) + " " + df[found_text_col].fillna("").astype(str)
    elif found_text_col:
        X = df[found_text_col].fillna("").astype(str)
    else:
        X = df[found_title_col].fillna("").astype(str)

    # Detect label column
    label_candidates = ["label", "target", "fake", "class", "is_fake"]
    found_label_col = None
    for col in df.columns:
        if col.lower().strip() in label_candidates:
            found_label_col = col
            break

    if not found_label_col:
        raise ValueError(
            f"Could not identify a label column in CSV with columns: {list(df.columns)}. "
            "Please ensure the CSV has a column named 'label' or 'target'."
        )

    # Normalize labels to 0 (genuine) and 1 (misleading/fake)
    y_raw = df[found_label_col]
    if y_raw.dtype == object:
        # String mapping
        mapping = {
            "fake": 1, "false": 1, "misleading": 1, "1": 1, 1: 1,
            "real": 0, "true": 0, "genuine": 0, "0": 0, 0: 0
        }
        y = y_raw.astype(str).str.strip().str.lower().map(mapping)
        if y.isna().any():
            valid_idx = y.notna()
            X = X[valid_idx]
            y = y[valid_idx].astype(int)
        else:
            y = y.astype(int)
    else:
        y = y_raw.astype(int)

    # Drop empty rows
    valid_text = X.str.strip().str.len() > 10
    X = X[valid_text]
    y = y[valid_text]

    return X, y
