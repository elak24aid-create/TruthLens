# TruthLens Backend — FastAPI & ML Service

TruthLens backend is a modular, high-performance REST API designed to provide explainable, multi-signal evidence assessment for suspicious news claims, headlines, and articles.

---

## Key Capabilities (Phase 1)

1. **Defensive Input Processing & Sanitization**: Strips malicious payloads, unescapes HTML, and analyzes structural characteristics.
2. **Multi-Script Language Detection**: Identifies English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Arabic, Spanish, and French using script ranges and linguistic markers.
3. **Stylistic Red Flag Analysis**: Detects capitalization shouting, repetitive emotional punctuation, and sensational viral clickbait buzzwords.
4. **Source Credibility & Transparency Lookup**: Evaluates domain attribution, HTTPS security, and known transparent publishers.
5. **Real ML Engine (TF-IDF + Logistic Regression)**: Trainable pipeline computing calibrated probabilities and influential feature attribution. Does not fabricate results when awaiting dataset training.
6. **Multi-Signal Evidence Aggregation**: Synthesizes inputs into explainable verdicts (`Likely Genuine`, `Likely Misleading`, `Unverified`, `Satire`, `Insufficient Evidence`) alongside a detailed "Why This Verdict?" breakdown.
7. **Rate Limiting & Defensive Exception Handling**: Prevents denial-of-service and hides raw server traces.

---

## Directory Layout

```
backend/
├── app/
│   ├── config.py              # Pydantic environment configuration
│   ├── main.py                # FastAPI app, CORS, rate limiting, exception handlers
│   ├── schemas/               # Request and response models
│   ├── routers/               # Health, Checker, and History endpoints
│   ├── services/              # Preprocessor, Language, Source Credibility, Evidence Aggregator
│   ├── ml/                    # Real ML Trainer, Predictor, and Evaluation
│   └── utils/                 # Sanitizer and Rate Limiter
├── tests/                     # Comprehensive pytest test suite
├── data/                      # Local storage for history & dataset
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup & Running

### 1. Python Environment

Ensure Python 3.10+ (tested on Python 3.14) is installed.

```bash
cd backend
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 4. Running the Server

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive Documentation:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 5. Running Tests

```bash
python -m pytest backend/tests -v
```

---

## ML Model Training Guide

To train the machine learning classifier with genuine data:

1. Obtain a legitimate benchmark dataset (e.g., WELFake or ISOT Fake News Dataset from Kaggle).
2. Save the CSV file to: `backend/data/news_dataset.csv`.
3. Ensure it has:
   - Text column: `text`, `content`, or `article` (or `title` + `text`)
   - Binary label column: `label` (0 = Real/Genuine, 1 = Fake/Misleading)
4. Execute training:
   ```bash
   python -m backend.app.ml.trainer
   ```
5. The script outputs real accuracy, precision, recall, F1-score, and confusion matrix, saving artifacts to `backend/app/ml/saved_models/`.
