# AI Codebase Assistant — Project Context

## Project Overview

### Project name
AI Codebase Assistant

### Goal
Build an AI assistant that can inspect a GitHub repository, understand its codebase using retrieval-augmented generation (RAG), and answer questions with relevant file and line references.

### Current status
As of September 4, 2026, the MVP is complete. The core RAG pipeline, FastAPI backend wrapper, and React frontend are working. The project is now in the polish phase.

### Main user flow

```text
GitHub URL
→ clone repository
→ scan/filter files
→ chunk code
→ local embeddings
→ ChromaDB
→ similarity search
→ grounded LLM answer
→ FastAPI JSON response
→ React Markdown-rendered answer with syntax-highlighted code + source references
```

---

## Current Technology Stack

- **Language:** Python
- **Backend:** FastAPI
- **Repository ingestion:** Git and GitHub URLs
- **Code chunking:** Custom Python chunker
- **Embeddings:** Sentence Transformers
- **Embedding model:** `all-MiniLM-L6-v2`
- **Embedding dimension:** 384
- **Vector database:** ChromaDB
- **LLM:** Groq — `openai/gpt-oss-120b`
- **Frontend:** React + Vite
- **Markdown rendering:** `react-markdown`
- **Markdown extensions:** `remark-gfm`
- **Code syntax highlighting:** `react-syntax-highlighter`

---

## Current Project Structure

```text
ai-codebase-assistant/
├── backend/
│   ├── ingestion/
│   │   ├── github.py
│   │   ├── file_loader.py
│   │   └── chunker.py
│   ├── rag/
│   │   ├── embeddings.py
│   │   └── vector_store.py
│   ├── test_pipeline.py
│   └── .env
├── frontend/
├── PROJECT_CONTEXT.md
└── HANDOFF.md
```

Preserve the existing structure unless a change is clearly required.

---

## Completed MVP

### End-to-end RAG pipeline

The complete pipeline is working:

1. Accept a GitHub repository URL.
2. Clone the repository.
3. Scan and filter source files.
4. Chunk code into meaningful sections.
5. Generate local embeddings.
6. Store embeddings/chunks in ChromaDB.
7. Perform similarity search.
8. Generate a grounded LLM answer.
9. Return the answer through FastAPI.
10. Render the answer in React with Markdown and syntax-highlighted code.
11. Display source-file references with line ranges.

### Backend API

The backend currently supports:

#### `POST /index`

Request:

```json
{
  "repo_url": "..."
}
```

Response includes:

- `repo_id`
- `files_scanned`
- `chunks_stored`

#### `POST /ask`

Request:

```json
{
  "repo_url": "...",
  "question": "..."
}
```

Response includes:

- `answer`
- `sources`

Each source contains:

- `file`
- `start_line`
- `end_line`

### React frontend

The frontend currently supports:

- GitHub repository URL input
- Repository indexing through `/index`
- Display of files scanned and chunks stored
- Question input
- Asking questions through `/ask`
- AI answer display
- Source files and line ranges
- Loading states
- Error messages
- Markdown rendering
- GitHub-style Markdown through `remark-gfm`
- Syntax-highlighted fenced code blocks using `react-syntax-highlighter`
- Plain inline code
- Dark code-block theme using `oneDark`
- Indexing-status guard

### Indexing-status guard

`App.jsx` tracks:

- `repoUrl` — the repository URL currently entered by the user
- `indexedRepoUrl` — the URL that was actually indexed

The **Ask Assistant** button is disabled whenever these URLs do not match, with an inline hint explaining that the current repository must be indexed first. This prevents questions from being sent against a stale or un-indexed repository.

---

## Important Technical Decisions

### Local embeddings

Use:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
```

The model produces 384-dimensional embeddings.

Reasons:

- Avoids OpenAI embedding API costs.
- Works locally.
- Suitable for the MVP.
- Supports both code-chunk and question embeddings.

### ChromaDB

All stored chunks and queries must use the same embedding model and dimension.

Do not mix:

- OpenAI embeddings
- Sentence Transformers embeddings

in the same ChromaDB collection.

If the embedding model changes, delete/recreate the affected ChromaDB collection or data before indexing again.

### LLM

The current LLM is:

```text
Groq
openai/gpt-oss-120b
```

The generated response must remain grounded in retrieved repository context.

### Markdown rendering

AI answers are rendered with `ReactMarkdown` and `remarkGfm`.

Fenced code blocks are syntax-highlighted with `react-syntax-highlighter` using the `oneDark` theme.

Do not use `dangerouslySetInnerHTML` for AI answers.

---

## CORS

Because Vite normally runs on port 5173 and FastAPI on port 8000, the backend must allow the frontend origin.

Current configuration:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Current Known Issues / Polish Items

The MVP is complete; these are improvements rather than blockers.

### 1. Chat-style layout
Convert the current single-question/single-answer experience into a running conversation layout.

### 2. Retrieval quality
Early tests showed distance scores around `1.7–1.9`. Check whether retrieval results are sufficiently relevant and whether a threshold or retrieval strategy improvement is needed.

Do not change the embedding model without a clear reason.

### 3. Answer/source layout
Clearly separate:

- user question
- AI answer
- source references

The source data is already returned and displayed; the remaining improvement is primarily visual/structural.

### 4. Re-indexing behavior
Detect when the same repository is indexed again and decide whether to warn, reuse, or explicitly replace existing indexed data.

Current behavior uses `add_chunks`; duplicate/re-index behavior has not been explicitly validated.

---

## Run Commands

### Backend

```bash
uvicorn main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

---

## Development Rules

1. Use this project context as the source of truth.
2. Make the smallest safe change first.
3. Do not assume a file exists without checking.
4. Preserve the current project structure unless there is a clear reason to change it.
5. Give exact terminal commands.
6. Explain errors in simple terms.
7. Do not mix unrelated Git repositories.
8. Do not pull from or use the old `Vigilant-AI` repository.
9. Never expose API keys in source code.
10. Keep `.env` in `.gitignore`.
11. Update `HANDOFF.md` after major work sessions.
12. When changing the embedding model, recreate the ChromaDB data.
13. Test each stage before adding the next feature.
14. Keep the MVP scope focused; do not add agents, automatic PRs, voice, authentication, or fine-tuning unless the scope is explicitly changed.

---

## MVP Scope Boundary

### Included

- GitHub URL input
- Repository cloning
- File scanning/filtering
- Code chunking
- Local embeddings
- ChromaDB storage
- Similarity search
- Grounded LLM question answering
- FastAPI API layer
- React frontend
- Markdown rendering
- Syntax-highlighted code
- File and line references
- Loading/error states
- Indexing-status protection

### Not included

- Autonomous agents
- Automatic pull requests
- Voice interaction
- Authentication
- Fine-tuning
- Advanced autonomous bug fixing
- Multi-user collaboration
- Complex non-MVP frontend features

---

## Immediate Next Goal

The end-to-end MVP is already working. The next work should therefore focus on polish and validation, in this order:

1. Improve the chat-style UI.
2. Validate retrieval quality and relevance.
3. Tighten separation of question, answer, and sources.
4. Validate and improve repository re-indexing behavior.
5. Keep testing after each change.

Do not treat the old goal of “complete one successful end-to-end pipeline run” as pending; it has been superseded by the current MVP-complete status.

---

## Handoff Alignment

`HANDOFF.md` is the operational handoff for the latest implementation state. This `PROJECT_CONTEXT.md` mirrors that state and should be updated whenever the architecture, completed features, known issues, constraints, or next steps materially change.

As of September 4, 2026:

```text
MVP STATUS: COMPLETE
CURRENT PHASE: POLISH
```
