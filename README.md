---
title: pdfagent
emoji: ✨
colorFrom: indigo
colorTo: pink
sdk: docker
app_port: 8501
pinned: false
license: mit
---

# pdfagent — PDF-Constrained Conversational Agent

A grounded chat agent for PDFs. Upload any document, ask questions about it,
get answers cited to specific pages and sections — and an explicit refusal
whenever the question goes outside the document.

Built for **STAIR x Scaler School of Technology, Task 3 (10 marks)**.

> **Runs entirely on free tiers.** LLM calls go to Groq's free API (Llama
> 3.3 70B + 3.1 8B Instant, no credit card required) and embeddings are
> local via `bge-m3`. No paid service is required to test or deploy.

## Demo

| | |
|---|---|
| Empty hero · gradient orb + suggestion cards | ![Hero](screenshots/01-hero.png) |
| Grounded answer with verbatim citation expander | ![Chat citation](screenshots/02-chat-citation.png) |
| Out-of-scope refusal with reason | ![Refusal](screenshots/03-refusal.png) |
| Live evaluation suite (5 in-scope + 3 OOS + Hindi bonus) | ![Eval](screenshots/04-eval.png) |
| Per-turn JSONL traces with retrieval scores + verifier | ![Traces](screenshots/05-traces.png) |

_Demo video: [add link after recording]_


> **Submission**
> - Repository: <https://github.com/dobbydobap/STAIRDigital-assessment>
> - Mail submission: `yashwardhansinghrathore1@gmail.com`, CC `saraffshubham@gmail.com`
> - Demo video: _<add link after recording>_

---

## How the rubric is met

| Rubric item | Where it lives |
|---|---|
| Accept any PDF | Streamlit upload + ingestion pipeline (text PDFs, tables, scanned PDFs via OCR fallback) |
| Answer only from the PDF | Hybrid retrieval + grounded-answer Llama 3.3 70B call + **deterministic verbatim-quote verifier** that rejects any quoted span not present on the cited page |
| Refuse out-of-scope queries | 4-category refusals: `out_of_scope`, `insufficient_evidence`, `partially_answerable`, `ambiguous` (plus `verification_failed` if even the verifier rejects) |
| Citations (page + section) | Every claim ends with `[p.N]`; each citation expands to show the verbatim quoted span and a rendered page image |
| Testability — 5 valid + 3 invalid queries | `eval/queries.yaml` (also includes a Hindi bonus query) |
| Observability | Per-turn JSONL trace at `data/traces/traces-YYYY-MM-DD.jsonl`, browsable via the **Traces** page in the UI |
| Deployed interface | Streamlit UI; Dockerfile and docker-compose for local; HF Spaces deploy notes below |
| **Bonus: multi-language** | bge-m3 multilingual embeddings + query-rewriter language detection + answers rendered in the question's language; verifier still runs against original-language source text |

---

## Architecture

```
        ┌──────────────────────────────────────────────────────────┐
        │                    Streamlit UI                          │
        │     Chat   ·   Eval suite (live)   ·   Traces            │
        └─────────────────────────┬────────────────────────────────┘
                                  │ direct call (no extra process)
                                  ▼
        ┌──────────────────────────────────────────────────────────┐
        │                    pdfagent.service                      │
        │       ingest_and_index(pdf)        chat(pdf_id, q)        │
        └───────────┬──────────────────────────────────┬───────────┘
                    │                                  │
                    ▼                                  ▼
   ┌──────────────────────────────┐     ┌──────────────────────────────┐
   │        Ingestion              │     │       Orchestrator           │
   │  PyMuPDF text + heading       │     │  rewrite → retrieve →        │
   │  Table extraction (md)        │     │  grounded-answer →           │
   │  OCR fallback (rapidocr)      │     │  verifier → trace            │
   │  Section-aware chunking       │     └──────┬───────────────┬──────┘
   └──────────────┬────────────────┘            │               │
                  ▼                              ▼               ▼
        ┌────────────────────┐   ┌────────────────────┐  ┌──────────────┐
        │   Index             │   │   Retrieve          │  │  Agent       │
        │   bge-m3 dense+sparse│   │   bge-m3 hybrid     │  │  Llama 3.3   │
        │   ChromaDB persist   │   │   sub-query fan-out │  │  70B (Groq)  │
        └────────────────────┘   └────────────────────┘  │  + 3.1 8B    │
                                                          │  for rewrite │
                                                          │  + Verifier  │
                                                          │  (verbatim)  │
                                                          └──────────────┘
```

Two boundaries are deliberate:

- **`agent/` is LLM-only**, **`retrieve/` and `verify.py` are deterministic.** Every layer is independently testable.
- The **verifier is Python, not an LLM**. It rejects any answer whose `quoted_span` doesn't appear verbatim on the cited page. That makes the anti-hallucination guardrail auditable rather than another model's opinion.

A FastAPI surface (`/upload`, `/chat`, `/pdfs`, `/page-image/{id}/{page}`, `/traces`, `/eval`) is also exposed for programmatic use, but the Streamlit UI imports the service directly so deploying is one process.

---

## Quickstart (local)

Requirements: Python 3.10+, ~3–4 GB free disk for model weights.

```powershell
git clone https://github.com/dobbydobap/STAIRDigital-assessment.git
cd STAIRDigital-assessment

python -m venv .venv
.venv\Scripts\Activate.ps1                 # Windows PowerShell
# source .venv/bin/activate                 # macOS / Linux

python -m pip install --upgrade pip
pip install -e ".[dev]"

copy .env.example .env                       # then edit .env to set GROQ_API_KEY
# cp .env.example .env                        # macOS / Linux
```

Run the UI:

```powershell
streamlit run pdfagent/ui/streamlit_app.py
```

Open <http://localhost:8501>. Upload a PDF in the sidebar, ask questions in the chat. Expand any citation to see the verbatim quote and the rendered page image.

(Optional) run the FastAPI surface alongside, on a different port:

```powershell
uvicorn pdfagent.api.app:app --port 8000
```

---

## Test instructions for evaluators

The eval suite at `eval/queries.yaml` defines 5 valid + 3 out-of-scope queries plus 1 Hindi bonus. They are intentionally generic so the same suite works against any reasonably structured PDF.

### 1. Drop a sample PDF

Save a structured PDF (research paper, policy doc, report — typically 10–50 pages) at:

```
eval/sample.pdf
```

The 8 rubric queries are written generically (title, authors, sections, summary, date, plus the OOS probes) so any structured PDF will work. NITI Aayog's _National Strategy for AI_, any government white paper, or an arXiv paper is a fine choice.

### 1a. (Optional) Run the preflight check

```powershell
python scripts/preflight.py
```

Confirms imports work, `GROQ_API_KEY` is set, and `eval/sample.pdf` exists before you run the live eval.

### 1b. (Optional) One-shot programmatic test

```powershell
python examples/quick_test.py eval/sample.pdf "What is this document about?"
```

Prints answer + citations + verifier verdict for a single question.

### 2. Run the suite (CLI)

```powershell
python eval/run_eval.py
```

This produces:

- `eval/report.md` — human-readable per-query report (PASS/FAIL, answer, citations, latency, tokens, cost)
- `eval/report.json` — same data as JSON
- exit code 0 if all 8 queries pass, 1 otherwise

### 3. Run the suite (UI)

Click **Eval** in the sidebar → **Run eval suite**. The page renders pass/fail with the verifier's per-citation results, the retrieved chunks' scores, and per-step latency.

### 4. Expected behaviour

| ID | Type | Query | Expected |
|---|---|---|---|
| V1 | in-scope | _What is the title or main heading of this document?_ | Answered with at least one cited verbatim quote |
| V2 | in-scope | _Who authored, prepared, or published this document?_ | Answered with citation |
| V3 | in-scope | _What are the main sections, chapters, or topics?_ | Answered with citations from multiple pages |
| V4 | in-scope | _Briefly summarize what this document is about._ | Answered with citation(s) |
| V5 | in-scope | _What date / year / version does the document state?_ | Answered with citation |
| O1 | out-of-scope | _What is the capital of France?_ | `scope=out_of_scope`, no answer, refusal_reason set |
| O2 | out-of-scope | _Will the policies described succeed over the next 10 years?_ | `out_of_scope` or `insufficient_evidence` (no speculation) |
| O3 | out-of-scope | _What is the personal birth date of the document's author?_ | `out_of_scope` or `insufficient_evidence` |
| B1 | bonus (multilingual) | _इस दस्तावेज़ का मुख्य विषय क्या है?_ | Hindi answer with citations to the (likely) English source |

### 5. Run the unit tests (offline, no API key needed)

```powershell
pytest tests/test_verify.py tests/test_chunk.py tests/test_llm_json.py -v
```

### 6. Run the live integration tests (hit Groq + bge-m3)

```powershell
$env:PDFAGENT_RUN_LIVE = "1"
pytest tests/test_eval_live.py -v
```

### 7. Demonstrate that grounding is real

Try a question whose answer the PDF doesn't contain — you should get a refusal that names what the PDF _does_ cover. Try a paraphrase attack ("rephrase this answer in your own words") — the verbatim verifier will reject any quoted span that isn't in the source.

---

## Deployment

### Docker

```powershell
docker build -t pdfagent:latest .
docker run --rm -p 8501:8501 -p 8000:8000 `
  -e GROQ_API_KEY=$env:GROQ_API_KEY `
  -v ${PWD}/data:/data `
  pdfagent:latest
```

Or use docker-compose (UI + API together):

```powershell
docker compose up --build
```

### Hugging Face Spaces (Docker SDK)

1. Create a new Space → SDK = **Docker**.
2. Push this repo to the Space's git remote.
3. In Space settings, add `GROQ_API_KEY` as a secret.
4. The included `Dockerfile` exposes 8501 (Streamlit) which Spaces will publish on the Space URL.

The Dockerfile pre-downloads the bge-m3 weights so cold starts on Spaces are sane.

---

## UI walkthrough

- **Chat** — upload a PDF or pick one from the sidebar, ask anything. Each assistant turn shows a row of pills (`in_scope`, `sufficient`, language, verifier status), a latency/token/cost line, and one expander per citation containing the verbatim quote and the cited page image.
- **Eval** — runs the rubric suite live and renders pass/fail with the verifier output and retrieved chunks per query.
- **Traces** — last N JSONL trace records: rewrite, retrieved chunks with dense/sparse/combined scores, sufficiency verdict, verifier output, latency, tokens. Includes raw JSON.

Color palette: see top of `pdfagent/ui/theme.py` (the "Monsoon" palette: deep midnight, teal primary, amber+mustard accents for citations).

---

## Technical note (decisions and trade-offs)

- **One LLM call for the answer, not two.** A second LLM verifier was tempting but adds 5–10 s of latency without being more defensible than a deterministic substring check. Verbatim-quote verification in Python is auditable — the failure mode is exactly the surface the rubric scores on.
- **bge-m3 hybrid (dense + sparse) instead of a separate cross-encoder.** bge-m3 returns both in one forward pass; combined with sub-query fan-out from the rewriter this reaches good recall without a heavyweight reranker. Add one only if eval recall starts missing.
- **Free-tier first.** LLM calls go to Groq's free API (Llama 3.3 70B for answers, Llama 3.1 8B Instant for query rewrites). Embeddings are local (`bge-m3`). The whole stack runs without paying any vendor — important for a student submission that has to be reproducible by graders. The LLM client is isolated to one file (`pdfagent/llm.py`) so swapping in Gemini, Anthropic, OpenAI, or a local model is a single-file edit (a Gemini reference adapter is included at `pdfagent/llm_groq.py` historically — see git history).
- **Sub-query rewriter, not a scope classifier.** The rewriter resolves coreferences, decomposes compound questions, and detects language; it intentionally does NOT decide whether the question is answerable. Scope is decided by the answerer, which has the retrieved evidence in front of it.
- **Page-image citation expanders.** Visible quoted span + page screenshot is what makes grounding feel real to a human evaluator. PyMuPDF's `page.get_pixmap()` is fast enough to cache lazily.
- **Refusal categories matter.** `out_of_scope` (general knowledge), `insufficient_evidence` (on-topic but missing), `partially_answerable` (compound), `ambiguous` (asks back), and a hard `verification_failed` floor when even the verifier rejects.
- **Multi-language path.** bge-m3 covers 100+ languages, so a Hindi question can retrieve from English chunks without translation. The answer is rendered in the question's language but the verifier always runs against the source-language text — so the citation chip preserves the original-language quote.
- **Persistence.** PDFs hash to a `pdf_id`; Chroma stores chunks under that id; the registry stores per-page text needed by the verifier; reuploads of the same file skip re-embedding.
- **What was deliberately cut.** No Langfuse (JSONL + the Traces page is enough), no cross-encoder rerank for v1, no conversation memory beyond the last 2 turns (the rewriter uses them only for coreference; retrieval re-runs each turn).

---

## Project layout

```
pdfagent/
├── ingest/      # PyMuPDF text + heading detection, tables, OCR, chunking
├── index/       # bge-m3 embedder + ChromaDB store
├── retrieve/    # query rewriter (Llama 3.1 8B) + hybrid fan-out
├── agent/       # grounded-answer Llama 3.3 70B call + verbatim verifier
├── trace/       # JSONL turn logger + cost aggregator
├── api/         # FastAPI app and routes
├── ui/          # Streamlit app + custom theme + eval/traces pages
├── service.py   # facade: ingest_and_index, chat
├── orchestrator.py # rewrite → retrieve → answer → verify pipeline
├── registry.py  # per-PDF metadata + page text store
├── llm.py       # Groq (Llama) client wrapper (the only provider-aware file)
├── config.py    # env-driven runtime config
└── types.py     # shared dataclasses

eval/            # queries.yaml, run_eval.py, sample.pdf (you supply)
tests/           # unit tests + live integration
```

---

## License & attribution

All code in this repository is the candidate's own work for the STAIR x Scaler assessment. The bge-m3 embedding model is © BAAI; PyMuPDF is licensed under AGPL-3.0; rapidocr-onnxruntime is Apache-2.0.
