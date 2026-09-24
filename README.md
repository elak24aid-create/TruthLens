# TruthLens — AI Fake News Detection Platform

> **"Check before you share."**  
> An AI-assisted cross-platform news verification and multi-signal evidence assessment platform designed for Android, iOS, and Web.

TruthLens does not claim that artificial intelligence can determine absolute truth with 100% certainty. Instead, it provides an evidence-based assessment framework combining statistical machine learning, linguistic and stylistic heuristic analysis, source credibility evaluation, and transparent citations to help users critically evaluate digital information.

---

## 🏗️ Architecture & Technology Stack

```
TruthLens/
├── backend/                  # Python + FastAPI REST API
│   ├── app/
│   │   ├── config.py         # BaseSettings configuration & environment variables
│   │   ├── main.py           # FastAPI entrypoint, CORS, rate limits, exception filters
│   │   ├── schemas/          # Pydantic schemas for Checker, History, Signals, Verdicts
│   │   ├── routers/          # Modular API routers (/health, /check-text, /history)
│   │   ├── services/         # Preprocessor, Language Detector, Source Credibility, Evidence Aggregator
│   │   ├── ml/               # Real ML Trainer, Evaluation, and Inference Predictor
│   │   └── utils/            # Sanitizer, Sliding-Window Rate Limiter
│   ├── tests/                # Pytest unit & integration test suite (13 passing tests)
│   ├── requirements.txt
│   └── .env.example
│
├── truthlens_app/            # Flutter Client Application (Material 3)
│   ├── pubspec.yaml          # Flutter dependencies
│   ├── lib/
│   │   ├── main.dart         # Entry point & dynamic theme switcher (Light / Dark)
│   │   ├── config/           # API and theme configurations
│   │   ├── core/             # Colors, typography, strings, network client
│   │   ├── models/           # Verdict, AnalysisResult, SignalItem, HistoryItem
│   │   ├── services/         # ApiService (REST), LocalHistoryService (Persistence)
│   │   ├── widgets/          # VerdictBadge, ConfidenceGauge, WhyVerdictCard, SkeletonLoader
│   │   └── features/
│   │       ├── shell/        # 4-tab bottom navigation bar
│   │       ├── home/         # Hero banner, quick check action, literacy guides
│   │       ├── checker/      # Dual Text/URL inputs, loading skeletons, Result screen
│   │       ├── history/      # Filterable local history, search, clear/delete
│   │       └── profile/      # Preferences, Dark Mode toggle, AI ethics disclosure
│   └── test/                 # Flutter model & widget tests
│
└── README.md
```

---

## ⚖️ Ethical AI & Verdict System

TruthLens rejects binary "100% True" or "100% Fake" declarations. Every analysis yields an evidence-based verdict accompanied by a confidence percentage and an expandable **"Why This Verdict?"** breakdown:

* **Likely Genuine**: High source transparency, neutral tone, standard editorial conventions.
* **Likely Misleading**: Stylistic red flags (excessive shouting, clickbait patterns, viral forward demands), unverified sources, or statistical classifier signals.
* **Unverified**: Inconclusive or conflicting signals requiring deeper primary documentation.
* **Satire**: Originating from recognized satirical publications (e.g. *The Onion*, *Babylon Bee*).
* **Insufficient Evidence**: Queries with insufficient text context or verifiable claims.

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.10+** (Tested on Python 3.14)
* **Flutter SDK 3.19+** (for building/running mobile & web apps)
* **Git**

---

### Step 1: Running the Backend

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
4. Start the FastAPI server:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
5. Test the live endpoints:
   - **Interactive API Documentation**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

6. Run Backend Tests:
   ```bash
   python -m pytest backend/tests -v
   ```

---

### Step 2: Training the ML Model (Real Data)

TruthLens strictly enforces no fabricated metrics or manufactured datasets.

1. Download a legitimate benchmark dataset (e.g., [WELFake](https://www.kaggle.com/datasets/saurabhshahane/fake-news-classification) or [ISOT](https://www.uvic.ca/engineering/ece/isot/datasets/fake-news/index.php)).
2. Place the CSV at: `backend/data/news_dataset.csv` (columns: `text` or `title` + `text`, and `label` where 0 = Genuine, 1 = Misleading).
3. Run the trainer:
   ```bash
   python -m backend.app.ml.trainer
   ```
4. The trainer computes real Accuracy, Precision, Recall, F1-Score, and Confusion Matrix, saving the trained model artifact to `backend/app/ml/saved_models/model.joblib`.

*Note: If no dataset is present, the backend gracefully falls back to linguistic heuristics and transparency signals without crashing or inventing fake accuracy numbers.*

---

### Step 3: Running the Flutter App

1. Navigate to `truthlens_app/`:
   ```bash
   cd truthlens_app
   ```
2. Fetch Flutter packages:
   ```bash
   flutter pub get
   ```
3. Run automated tests:
   ```bash
   flutter test
   ```
4. Launch on Android, iOS, or Chrome:
   ```bash
   # Run on connected device or emulator:
   flutter run

   # Or run on Chrome Web:
   flutter run -d chrome --dart-define=API_BASE_URL=http://127.0.0.1:8000/api
   ```

---

## 🔒 Security & Best Practices

- **Zero Hardcoded Secrets**: Secrets and configurations are loaded via environment variables.
- **Defensive Input Sanitization**: HTML stripping and character normalizing before processing.
- **Sliding-Window Rate Limiting**: Protects backend endpoints against brute-force flooding.
- **CORS Protection**: Explicit allowed origin middleware.
- **Fail-Safe UI**: Graceful network error states, timeout handlers, and offline local caching.

---

## 🗺️ Roadmap

- [x] **Phase 1 (Completed)**:
  - Modular FastAPI architecture with health, checker, and history endpoints.
  - Multi-script language detection (English, Tamil, Hindi, Arabic, Spanish, etc.).
  - Stylistic pattern extraction (ALL CAPS, emotional punctuation, buzzwords).
  - Trainable TF-IDF + Logistic Regression ML pipeline with feature attribution.
  - Multi-signal evidence aggregation with "Why This Verdict?".
  - Full Flutter Material 3 client (Home, Check News, History, Profile).
  - Backend test suite (13 passing tests).
- [ ] **Phase 2**:
  - Firebase Authentication & Google Sign-In.
  - Cloud Firestore history synchronization.
  - Google Fact Check Tools API deep integration.
  - Enhanced URL scraping with readability fallback.
- [ ] **Phase 3**:
  - Reverse image verification & manipulated media indicators.
  - Android/iOS Share Sheet integration.
  - Community reporting with moderation queue.
