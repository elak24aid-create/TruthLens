# TruthLens Google Cost Safety

## Free Default Guarantee
TruthLens guarantees usability at ₹0/$0 without requiring paid Gemini billing.

### Mechanisms:
- **Daily Hard Limits**: The system enforces a strict daily limit on Google Search Grounding calls using a local JSON tracker (`google_usage.json`). Once the limit is reached, it automatically falls back to free web scraping. (LOCAL_REQUEST_LIMIT: ENFORCED).
- **Billing**: PAID_BILLING_PREVENTION: NOT_GUARANTEED_BY_LOCAL_COUNTER. A local counter alone does not guarantee zero financial cost if billing is enabled on the cloud project.
- **Model Selection**: Uses `gemini-3.5-flash-lite`, the most cost-effective and capable free model that supports Search Grounding.
- **API Optionality**: Google APIs are fully optional. If `GOOGLE_API_KEY` is not provided or the limit is hit, TruthLens remains fully functional using the hybrid fallback pipeline.
- **Fact Check Priority**: The Google Fact Check Tools API is prioritized as the first step since it's highly relevant and completely free.
