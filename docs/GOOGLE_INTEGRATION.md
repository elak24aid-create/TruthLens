# TruthLens Google Integration

## Hybrid Architecture
TruthLens uses a cascading hybrid architecture to balance veracity and cost safety.

The priority pipeline is as follows:
1. **Google Fact Check Tools API:** The most authoritative and free source. 
2. **Gemini 3.5 Flash Lite + Google Search Grounding:** If no direct fact-check is found, TruthLens uses structured output with Google Search to analyze the claim multimodally.
3. **DuckDuckGo Web Search Fallback:** If the free daily quota for Google is exhausted, the system seamlessly falls back to free web scraping and analysis.
4. **Local ML Baseline:** If all external lookups fail (or the device is offline), the system resorts to the TF-IDF model.

## Multimodality
The Gemini integration handles text directly, while for images and video, OCR text and metadata are extracted locally and supplied to the pipeline as fallback/text signal.
