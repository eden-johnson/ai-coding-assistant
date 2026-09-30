# AI Codebase Assistant

Ask questions about any public GitHub repository and get answers grounded in the actual code, with file paths and line numbers as references.

The app clones a repository, splits its source into chunks, embeds them locally, and stores them in a vector database. When you ask a question, it retrieves the most relevant chunks and has an LLM answer using only that code.

## Features

- **Index any public GitHub repo** by pasting its URL
- **Semantic code search** using local embeddings (no embedding API costs)
- **Grounded answers** generated from retrieved code only, with citations to file and line range
- **Source list** showing the top matching chunks for every answer
- **Per-repo isolation**: each repository gets its own ChromaDB collection, so results never mix
- **Persistent index**: embeddings are saved to disk, so you only index a repo once
- **Clean React UI** with Markdown-rendered answers

## How it works

```
GitHub URL
    │
    ▼
Shallow clone (GitPython, depth=1)
    │
    ▼
Scan files (skips .git, node_modules, venv, dist, build, ...)
    │
    ▼
Chunk (60 lines per chunk, 10-line overlap, line numbers kept)
    │
    ▼
Embed locally (sentence-transformers, all-MiniLM-L6-v2)
    │
    ▼
Store in ChromaDB (one collection per repo, persisted to ./chroma_db)

Question ──► embed ──► top 3 similar chunks ──► Groq LLM ──► answer + sources
```

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19, Vite, react-markdown, remark-gfm |
| API | FastAPI, Uvicorn, Pydantic |
| Ingestion | GitPython, custom file scanner and line-based chunker |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`), runs locally |
| Vector store | ChromaDB (persistent) |
| LLM | Groq API (`openai/gpt-oss-120b`) |

## Project structure

```
ai-coding-assistant/
├── backend/
│   ├── main.py               # FastAPI app: /index and /ask endpoints
│   ├── test_pipeline.py      # End-to-end CLI test of the full pipeline
│   ├── requirements.txt
│   ├── ingestion/
│   │   ├── github.py         # Clone and clean up repositories
│   │   ├── file_loader.py    # Walk the repo and read source files
│   │   └── chunker.py        # Split files into overlapping chunks
│   └── rag/
│       ├── embeddings.py     # Local sentence-transformers embeddings
│       ├── vector_store.py   # ChromaDB storage and similarity search
│       └── llm.py            # Prompt construction and Groq call
└── frontend/
    ├── src/
    │   ├── App.jsx           # Main UI
    │   └── main.jsx
    └── package.json
```

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- A [Groq API key](https://console.groq.com/)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
GROQ_API_KEY=your_api_key_here
```

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

The first run downloads the embedding model, so it may take a moment.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173). The backend allows CORS from `localhost:5173` and `127.0.0.1:5173`; edit `allow_origins` in `backend/main.py` if your frontend runs on another port. The frontend expects the API at `http://localhost:8000`; change `API_URL` in `frontend/src/App.jsx` if you run it elsewhere.

### 3. Use it

1. Paste a GitHub repository URL and click **Index Repository**.
2. Wait for the file and chunk counts to appear.
3. Ask a question such as *"Where is the application initialized?"* and click **Ask Assistant**.

## API reference

### `POST /index`

Clones, chunks, embeds, and stores a repository.

```json
{ "repo_url": "https://github.com/user/project" }
```

Response:

```json
{ "repo_id": "user-project", "files_scanned": 42, "chunks_stored": 310 }
```

### `POST /ask`

Answers a question about an indexed repository.

```json
{ "repo_url": "https://github.com/user/project", "question": "How is authentication handled?" }
```

Response:

```json
{
  "answer": "Authentication is handled in ...",
  "sources": [
    { "file": "src/auth.py", "start_line": 1, "end_line": 60 }
  ]
}
```

## Test from the command line

Run the whole pipeline without the UI:

```bash
cd backend
python test_pipeline.py https://github.com/user/project "What does the main module do?"
```

## Current limitations

- **Python only**: the scanner currently indexes `.py` files. Support for other languages means extending `ALLOWED_EXTENSIONS` in `ingestion/file_loader.py`.
- **Public repos only**: cloning uses plain HTTPS without authentication.
- **Fixed-size chunking**: chunks are split by line count, not by function or class boundaries.
- **Top 3 retrieval**: answers draw on the three most similar chunks, which can miss context for broad questions.
- **Re-indexing replaces data**: indexing a repo again wipes its previous collection and rebuilds it from the latest code.

## Roadmap

- [ ] Multi-language support
- [ ] Syntax-aware chunking (functions and classes)
- [ ] Private repositories via access tokens
- [ ] Configurable number of retrieved chunks
- [ ] Conversation history and follow-up questions
- [ ] Streaming answers

## License

Add a license of your choice (for example MIT).
