# Civil Guru 🏛️

**AI-powered UPSC exam preparation assistant**: four retrieval-augmented agents built on a RAG pipeline with Qdrant Cloud and Groq, deployed live on Streamlit Community Cloud.

**Live app:**  https://civil-guru-ai-wrdivsydaysa5pfgkexzgm.streamlit.app

---

## What it does

Civil Guru is a study tool for UPSC (Indian Civil Services) aspirants, built around four independent agents that share a common retrieval backend:

| Agent | What it does |
|---|---|
| **Syllabus Mapper** | Maps a current-affairs topic to the relevant UPSC GS Paper (1–4) and subject, with sourced context and related topics |
| **Fact Checker** | Verifies a claim against official PIB (Press Information Bureau) and PRS (Legislative Research) sources, returns PASS/FAIL/PARTIAL with reasoning |
| **Answer Evaluator** | OCR-reads a photo of a handwritten UPSC Mains answer and scores it out of 15 against a rubric (introduction, structure, dimensions, facts, analysis, conclusion) |
| **Answer Generator** | Writes a full structured UPSC Mains model answer (Introduction–Body–Conclusion) grounded in retrieved context |

---

## Architecture

```
Streamlit UI (app.py)
        │
        ├── Syllabus Mapper ──┐
        ├── Fact Checker ─────┤
        ├── Answer Evaluator ─┼──► Qdrant Cloud (vector search)
        └── Answer Generator ─┘         │
                                         ▼
                              sentence-transformers
                              (all-MiniLM-L6-v2, 384-dim)
                                         │
                                         ▼
                         cross-encoder reranker
                         (ms-marco-MiniLM-L-6-v2)
                                         │
                                         ▼
                              Groq API (openai/gpt-oss-20b)
                              → generation / evaluation / verdicts
```

**Retrieval:** ~32,000 chunks across three collections in Qdrant Cloud —
- `civil_guru` (29,879 chunks — NCERT textbooks, subject-tagged: Polity, History, Economics, Geography, Ethics, Sociology, Art & Culture)
- `pib_articles` (915 chunks — official government press releases)
- `prs_articles` (1,100 chunks — legislative research)

**Generation:** Groq's `openai/gpt-oss-20b`, a reasoning model — tuned with `reasoning_effort="low"` and increased `max_tokens` budgets to leave enough room for the actual answer after the model's internal reasoning pass.

**No separate backend.** Streamlit runs the Python application logic directly — there's no separate API server; `app.py` is both interface and application code in a single process.

**Stateless by design.** Each request (a topic, a claim, a question) is handled independently with no session memory. The app doesn't track conversation history between queries — every query starts fresh.

---

## Tech stack

- **Frontend:** Streamlit
- **Vector database:** Qdrant Cloud (free tier)
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions, cosine similarity)
- **Reranking:** cross-encoder (`ms-marco-MiniLM-L-6-v2`)
- **LLM inference:** Groq API (`openai/gpt-oss-20b`)
- **OCR:** Tesseract (via `pytesseract`) — local only, see limitations below

---

## Engineering notes

**Migrated from local ChromaDB → Qdrant Cloud.** The original prototype ran entirely on a local persistent ChromaDB store, which isn't viable for a hosted deployment. All three collections were migrated with a batched, idempotent script (`SCRIPTS/day38_migrate_to_cloud.py`) that verifies chunk counts post-migration and preserves existing embeddings without re-embedding, to avoid any drift from the already-validated local vectors.

**Centralized retrieval and generation.** Rather than duplicate Qdrant/Groq client setup across four separate agent files, both are centralized in shared modules (`qdrant_client_setup.py`, `groq_client_setup.py`) that every agent imports from — reducing duplicated logic and giving a single point of control for connection settings, timeouts, and model selection.

**Ollama → Groq for hosted inference.** The original prototype used a local Ollama instance (`llama3.2:3b`), which isn't available on Streamlit Cloud's servers. Switched to Groq's hosted API. Discovered along the way that `gpt-oss-20b` is a reasoning model that spends part of its token budget on an internal reasoning trace before producing output — an early test returned an empty response because `max_tokens` was too low to cover both. Fixed by setting `reasoning_effort="low"` and increasing token budgets across all four agents.

---

## Known limitations

- **Retrieval quality on specific factual queries.** Semantic search sometimes surfaces topically-adjacent chunks rather than an exact match for narrow queries (e.g. a specific constitutional article) when the knowledge base doesn't have a strong distinct chunk for that exact topic. This is a property of embedding-based retrieval, not a migration bug — same behavior would occur on the original local setup.
- **Blank/placeholder chunks in the dataset.** A regex-based filter to detect and exclude blank chunks (from extraction gaps in the original PDF processing) was built but not yet applied to the production Qdrant data — planned as a future data-quality pass.
- **Subject-detection confidence.** The embedding-based subject classifier occasionally misclassifies borderline questions (e.g. a judiciary/governance question tagged as Sociology instead of Polity) with low confidence scores. The underlying answer generation is unaffected, but the subject badge shown to the user can be inaccurate in these cases.
- **OCR (Answer Evaluator) is local-only.** Tesseract OCR requires a system-level binary that isn't installed on Streamlit Cloud by default. The app detects the platform and skips the hardcoded local path on non-Windows systems, but the OCR feature itself will not function on the hosted deployment until a `packages.txt` entry (`tesseract-ocr`) is added for Streamlit Cloud's Debian environment.

---

## Running locally

```bash
pip install -r requirements.txt
```

```bash
cd SCRIPTS
streamlit run app.py
```
