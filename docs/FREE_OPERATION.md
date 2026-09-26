# TruthLens Free-First Operation

## Mandatory Costs
- **Mandatory Operating Cost**: ₹0 / $0
- **Paid API Required**: NO
- **Gemini Required**: NO
- **Google Search Grounding Required**: NO

## Free Features Used
- **Google News / Public RSS**: YES (Used purely for information discovery, not as direct proof)
- **Public Web Research (DDGS)**: YES (Used for free search fallback)
- **Local ML (TF-IDF)**: YES (Offline fallback)

## Verification Pipeline
The system operates securely and cost-effectively by defaulting to free methods:
1. **Claim Extraction**
2. **Google News/RSS Discovery**
3. **Public Web Research (DuckDuckGo)**
4. **Public Fact-Check Sources (When available for free)**
5. **Local Evidence Aggregation & TF-IDF Secondary Signal**
6. **Transparent Verdict Generation**

## Limitations
- Performance relies heavily on public-source availability and is subject to public rate limits (e.g. DDGS).
- Real-world processing constraints apply; there is no "unlimited" usage or "100% accuracy" guarantee.
