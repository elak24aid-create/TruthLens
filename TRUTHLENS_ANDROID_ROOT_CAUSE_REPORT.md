LOGIN_ROOT_CAUSE:
The `MainNavigationScaffold` uses a Flutter `IndexedStack` which instantiates all 5 tabs immediately upon rendering. `HomeScreen`, `HistoryScreen`, and `CommunityReportsScreen` all run their `initState` simultaneously on login, firing massive concurrent HTTP requests. This overwhelms the Render backend, causing the app to hang or timeout on cold starts.

TEXT_ROOT_CAUSE:
The backend `online_research.py` relies entirely on naive regular expressions (e.g., `\b(fact\s*check(ed)?:?\s*(false|fake|misleading))\b`) to classify DuckDuckGo search snippets. If a search result doesn't contain these exact keywords, it is marked as `context`. The aggregator then ignores it, defaulting almost every query (both true and false) to "Insufficient Evidence".

URL_ROOT_CAUSE:
In `checker.py`, the URL analysis correctly extracts the article, but it defines the search `query_text` as the first 300 characters of the raw extracted body (`preprocessed["cleaned_text"][:300]`). DuckDuckGo returns 0 results for a massive paragraph query, causing an instant failure.

NEWS_ROOT_CAUSE:
The backend `news.py` failed to enforce the 1-hour staleness rule. It caches RSS results but doesn't explicitly filter out older articles by parsing their `published_parsed` timestamp against `utcnow() - timedelta(hours=1)`.

OPEN_SOURCE_ROOT_CAUSE:
In `result_screen.dart`, the "Open Source" button calls `if (await canLaunchUrl(url)) { launchUrl(url); }`. If `canLaunchUrl` fails (due to invalid URLs or Android 11+ intent query restrictions), it silently does nothing. There is no `else` block or `SnackBar` to warn the user.

IMAGE_ROOT_CAUSE:
The backend successfully extracts OCR text, but Flutter's `ResultScreen.dart` was hardcoded to print `widget.originalText` (which is passed in as the image's filename) instead of mapping to `result.extractedMetadata['ocr_text']`. The user never sees the extracted text.

VIDEO_ROOT_CAUSE:
Identical to the Image root cause. The UI displays the local video filename instead of the frame-extracted OCR text.

LOGIN_TIMING: ~30s (timeout/hang)
TEXT_TIMING: 1.5s - 25.8s
URL_TIMING: ~16.8s
NEWS_TIMING: ~6.8s
IMAGE_TIMING: ~3-5s (plus upload)
VIDEO_TIMING: ~5-8s

FRONTEND_BACKEND_MISMATCHES:
The backend `checker.py` attempts to attach `title`, `source_name`, `url`, and `published_at` to the `ExtractedMetadata` object during URL checking. However, the Pydantic schema `ExtractedMetadata` does not define these fields, so they are silently discarded. The Flutter app expects them (`result.extractedMetadata!['title']`), resulting in missing UI data.

FACT_CHECK_LOGIC_PROBLEM:
The system is entirely reliant on keyword overlap rather than semantic claim/evidence comparison. Because `online_research.py` uses hardcoded regex to determine if evidence is `supporting` or `conflicting`, claims like "The Sun is a star" return 5 `context` sources and 0 `supporting` sources, leading to a false "Insufficient Evidence" verdict.

RECOMMENDED_FIX_ORDER:
1. Fix Pydantic schema `ExtractedMetadata` to include dynamic fields or explicitly add `title`/`source_name` (Frontend/Backend contract).
2. Fix `online_research.py` to use an LLM or semantic classifier instead of naive regex, allowing true semantic fact-checking.
3. Fix `checker.py` to use the article title/headline for DDGS queries instead of the first 300 characters of the body.
4. Fix Flutter `MainNavigationScaffold` to use lazy-loading for the `IndexedStack` to prevent login congestion.
5. Fix `ResultScreen.dart` to actually display `ocr_text` and add visible error handling to `url_launcher`.
6. Fix `news.py` to rigorously filter out RSS entries older than 1 hour.

CRITICAL_BLOCKERS:
- The naive regex matching in `online_research.py` completely destroys the app's ability to verify real-world claims.
- The `IndexedStack` concurrency bomb guarantees a terrible login experience on Android.

DO_NOT_FIX_YET:
YES

PROJECT_STATUS:
NEEDS_ROOT_CAUSE_FIX
