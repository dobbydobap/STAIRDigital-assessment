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

# pdfagent

A chat agent that answers questions about a PDF you upload. It only uses the PDF as a source. Every claim it makes is tied to a page, with the exact quoted line shown. If you ask something the document doesn't cover, it refuses and explains why.

Built for **STAIR x Scaler School of Technology — Task 3 (10 marks)**.

- **Live demo:** _add HuggingFace Spaces URL here_
- **Demo video:** _add YouTube/Drive link here_
- **Repo:** https://github.com/dobbydobap/STAIRDigital-assessment

Submission to `yashwardhansinghrathore1@gmail.com`, CC `saraffshubham@gmail.com`.

---

## What it does

1. You upload a PDF.
2. The PDF is parsed (text, headings, tables, scanned pages via OCR if needed) and split into section-aware chunks.
3. Each chunk is embedded with `bge-m3`, which is multilingual and gives both dense and sparse vectors. They go into a local ChromaDB index.
4. When you ask a question:
   - A small Llama model rewrites the query so coreferences ("that table") are resolved and the question is split if it has multiple parts. It also detects the question's language.
   - The retriever pulls the top chunks using a hybrid score (dense + sparse).
   - A larger Llama model writes an answer in JSON: scope, sufficiency, the answer text, the citations (page + section + verbatim quoted line), and a refusal reason if it can't answer.
   - A short Python verifier checks that every quoted line actually appears on the cited page. If a quote isn't in the document word-for-word, the answer is regenerated once. If it still fails, the agent refuses rather than guess.
5. The answer is rendered with inline `[p.N]` chips. Each citation expands to show the verbatim quote and a screenshot of the cited page.

The whole stack runs on free tiers — Groq for the LLM (no card required) and `bge-m3` running locally for embeddings.

---

## Refusal types

- `out_of_scope` — the question isn't about the PDF (general knowledge, opinion, prediction). The agent tells you what topics the PDF *does* cover.
- `insufficient_evidence` — on topic but the PDF doesn't have the specific fact. The agent says what it found in the same area.
- `partially_answerable` — compound question. Answers what it can, refuses the rest, in one reply.
- `ambiguous` — multiple plausible meanings. Asks one clarifying question.
- `verification_failed` — internal floor. Triggers when the verifier can't validate any quote after one retry.

---

## Demo

| | |
|---|---|
| Empty hero with the suggestion cards | ![Hero](screenshots/01-hero.png) |
| A grounded answer with one citation expander open | ![Citation](screenshots/02-chat-citation.png) |
| Out-of-scope refusal | ![Refusal](screenshots/03-refusal.png) |
| Live evaluation page (5 in-scope + 3 out-of-scope + Hindi bonus) | ![Eval](screenshots/04-eval.png) |
| Per-turn traces with retrieval scores and verifier output | ![Traces](screenshots/05-traces.png) |

---

## Quick start (local)

Python 3.10+ and around 4 GB of free disk for the embedding model and Python deps.

```powershell
git clone https://github.com/dobbydobap/STAIRDigital-assessment.git
cd STAIRDigital-assessment

python -m venv .venv
.venv\Scripts\Activate.ps1            # PowerShell
# source .venv/bin/activate            # macOS / Linux

python -m pip install --upgrade pip
pip install -e ".[dev]"

copy .env.example .env                  # then edit and put your real Groq key in GROQ_API_KEY
```

Get a free Groq key at https://console.groq.com/keys. Paste it into `.env`.

Run the UI:

```powershell
streamlit run pdfagent/ui/streamlit_app.py
```

Open http://localhost:8501. Upload a PDF in the sidebar and start asking.

The FastAPI surface is also available if you want to test the endpoints directly:

```powershell
uvicorn pdfagent.api.app:app --port 8000
```

Endpoints: `/upload`, `/chat`, `/pdfs`, `/page-image/{id}/{page}`, `/traces`, `/eval`.

---

## How to reproduce the rubric tests

The 8 rubric queries plus a Hindi bonus query live in `eval/queries.yaml`. They're written generically (title, authors, sections, summary, date, three OOS probes, one Hindi question) so the same suite works for any structured PDF.

### 1. Drop a sample PDF

Save any PDF (research paper, government policy doc, report — usually 10 to 50 pages) at:

```
eval/sample.pdf
```

If you want a known-good one, NITI Aayog's *National Strategy for AI* works well:

```powershell
Invoke-WebRequest `
  -Uri "https://www.niti.gov.in/sites/default/files/2023-03/National-Strategy-for-Artificial-Intelligence.pdf" `
  -OutFile "eval\sample.pdf"
```

### 2. Run the suite

```powershell
python scripts/preflight.py     # checks imports + key + sample.pdf
python eval/run_eval.py
```

Outputs:
- `eval/report.md` — readable per-query report
- `eval/report.json` — same data as JSON
- exit 0 if all pass, 1 otherwise

The first run downloads `bge-m3` weights (~2 GB). One-time cost.

### 3. Or run the suite from the UI

Click **Eval** in the sidebar, then **Run eval suite**. Same code path as the CLI.

### 4. The 9 queries and what each one tests

| ID | Type | Query | Expected |
|---|---|---|---|
| V1 | in scope | What is the title or main heading of this document? | answered with citation |
| V2 | in scope | Who authored, prepared, or published this document? | answered with citation |
| V3 | in scope | What are the main sections, chapters, or topics? | answered with citations across pages |
| V4 | in scope | Briefly summarize what this document is about. | answered with citation |
| V5 | in scope | What date, year, or version does the document state? | answered with citation |
| O1 | out of scope | What is the capital of France? | refused as out_of_scope |
| O2 | out of scope | Will the policies described succeed over the next 10 years? | refused (out_of_scope or insufficient) |
| O3 | out of scope | What is the personal birth date of the document's author? | refused (out_of_scope or insufficient) |
| B1 | bonus | इस दस्तावेज़ का मुख्य विषय क्या है? | Hindi answer with English-source citations |

### 5. Unit tests (no key needed)

```powershell
pytest tests/test_verify.py tests/test_chunk.py tests/test_llm_json.py -v
```

Tests the verifier, the chunker, and JSON extraction. No Groq calls, no model download.

### 6. Live integration tests (uses your Groq key)

```powershell
$env:PDFAGENT_RUN_LIVE = "1"
pytest tests/test_eval_live.py -v
```

---

## Project layout

```
pdfagent/
├── ingest/      PyMuPDF text + heading detection, tables, OCR fallback, section-aware chunking
├── index/       bge-m3 embedder + ChromaDB store, persisted by file hash
├── retrieve/    Llama 3.1 8B query rewriter (coref, decomposition, language) + hybrid retriever
├── agent/       grounded-answer Llama 3.3 70B call + verbatim-quote verifier
├── trace/       JSONL turn logger + token / cost aggregator
├── api/         FastAPI app and routes
├── ui/          Streamlit app with chat, eval, and traces pages
├── service.py   facade: ingest_and_index, chat
├── orchestrator.py   pipeline: rewrite → retrieve → answer → verify
├── registry.py  per-PDF metadata + per-page text store
├── llm.py       Groq client wrapper (only file that knows the LLM provider)
├── config.py    env-driven runtime config
└── types.py     shared dataclasses

eval/            queries.yaml, run_eval.py, sample.pdf (you supply)
tests/           unit tests + gated live integration tests
```

The `agent/` module is the only place that talks to an LLM. The `retrieve/` and `agent/verify.py` modules are deterministic. That separation makes each layer independently testable and the verifier auditable.

---

## What I picked and why

- **One LLM call for the answer, not two.** A second LLM "judge" was tempting but slow and not actually more defensible than a literal Python check. The verifier checks that every quoted line in the answer appears word-for-word on the cited page. If it doesn't, the agent regenerates once. If it still fails, the agent refuses. That's the anti-hallucination guardrail.

- **bge-m3 hybrid retrieval, no separate reranker.** bge-m3 returns dense and sparse scores in a single forward pass. A combined score is enough for documents up to a few hundred pages. A reranker would add complexity without clear gains here.

- **Sub-query rewriter, not a scope classifier.** The rewriter resolves coreferences and detects language. It does not decide if a question is answerable. That decision belongs to the answerer because it has the retrieved evidence in front of it.

- **Page-image citation expanders.** Showing the verbatim quote *and* a screenshot of the cited page makes grounding feel real to a human reader. PyMuPDF's `page.get_pixmap()` is fast enough to cache per page.

- **Free-tier first.** LLM via Groq (Llama 3.3 70B for answers, 3.1 8B Instant for rewrites). Embeddings local via bge-m3. No API key needed beyond Groq, which is free with no card. The whole setup is reproducible by anyone grading this submission.

- **What I cut.** Hosted observability (Langfuse). A second LLM verifier. Cross-encoder reranker. Conversation memory beyond the last 2 turns. None of these would change the rubric outcome.

---

## Deploy

The Dockerfile bakes in the bge-m3 weights so cold start is reasonable. To deploy on Hugging Face Spaces:

1. Create a Space with SDK = Docker.
2. Push this repo to the Space's git remote.
3. In Space settings, add `GROQ_API_KEY` as a secret.
4. The Streamlit UI is exposed on port 8501 (matches the front-matter in this README).

To run locally with Docker:

```powershell
docker build -t pdfagent:latest .
docker run --rm -p 8501:8501 `
  -e GROQ_API_KEY=$env:GROQ_API_KEY `
  -v ${PWD}/data:/data `
  pdfagent:latest
```

---

## License and attribution

Code is the candidate's own work. `bge-m3` is © BAAI. PyMuPDF is AGPL-3.0. `rapidocr-onnxruntime` is Apache-2.0. Groq's Llama 3 models are subject to Meta's Llama license.
