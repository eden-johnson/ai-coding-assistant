# HANDOFF.md

## Current Status

As of September 4, 2026, the core RAG pipeline, FastAPI backend wrapper, and React frontend are working — MVP complete. Now in polish phase.

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

## Backend

The backend supports:

- `POST /index`
  - Request: `{ "repo_url": "..." }`
  - Response: `repo_id`, `files_scanned`, and `chunks_stored`
- `POST /ask`
  - Request: `{ "repo_url": "...", "question": "..." }`
  - Response: `answer` and `sources`
  - Each source contains `file`, `start_line`, and `end_line`

The backend uses Sentence Transformers with `all-MiniLM-L6-v2` embeddings of dimension 384, ChromaDB, and Groq model `openai/gpt-oss-120b`.

Do not mix embedding models or dimensions in the same ChromaDB collection. Never commit `.env` or API keys.

## React Frontend

The React frontend was created with Vite and currently supports:

- GitHub repository URL input
- Repository indexing through `/index`
- Displaying files scanned and chunks stored
- Question input
- Asking questions through `/ask`
- Displaying AI answers
- Displaying source files and line ranges
- Loading states
- Error messages
- **Indexing-status guard:** "Ask Assistant" is disabled, with an inline hint, whenever the current repo URL doesn't match the last-indexed URL — prevents asking against a stale or un-indexed repo
- **Syntax-highlighted code blocks** in AI answers (dark theme), via `react-syntax-highlighter`; inline code stays plain

Frontend stack:

```text
React
Vite
react-markdown
remark-gfm
react-syntax-highlighter
```

## Markdown Rendering

Markdown rendering was added to the AI answer section, along with syntax highlighting for fenced code blocks.

Installed packages:

```bash
npm install react-markdown remark-gfm
npm install react-syntax-highlighter
```

The answer is rendered using:

```jsx
<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  components={{
    code({ inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || "");
      return !inline && match ? (
        <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" {...props}>
          {String(children).replace(/\n$/, "")}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
  }}
>
  {answer}
</ReactMarkdown>
```

Supported formatting includes headings, paragraphs, bold and italic text, lists, inline code, fenced code blocks (syntax-highlighted, dark theme via `oneDark`), tables, blockquotes, and GitHub-style Markdown.

Markdown styles were added to `src/App.css` for headings, lists, code blocks, tables, links, and blockquotes. A `.hint-text` style was added for the indexing-status guard message.

Do not use `dangerouslySetInnerHTML` for AI answers.

## Indexing-Status Guard

`App.jsx` tracks `indexedRepoUrl` (the URL that was actually indexed) separately from `repoUrl` (the current input value). The "Ask Assistant" button is disabled whenever these two don't match, with a gray hint line explaining why. This closes a gap where changing the URL field after indexing could let a user ask a question against the wrong (or no) index.

## CORS

Because Vite normally runs on port 5173 and FastAPI on port 8000, the backend must allow:

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

## Run Commands

Backend:

```bash
uvicorn main:app --reload
```

Frontend:

```bash
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

Backend URL: `http://localhost:8000`

## Next Steps

1. Chat-style layout (bigger change — turn single Q&A into a running conversation).
2. Improve retrieval quality if returned chunks are not relevant (distance scores were ~1.7–1.9 on early tests; worth checking if that's a good threshold).
3. Clearly separate the user question, AI answer, and source references (visual/structural, not just data — currently source refs already shown, but layout could be tightened).
4. Add repo re-indexing detection (e.g. warn if the same repo is indexed twice — currently just re-adds/overwrites via `add_chunks`, not explicitly tested for duplicate behavior).

## Constraints

- Use the project context as the source of truth.
- Make the smallest safe change.
- Do not add non-MVP features such as agents, PRs, voice, authentication, or fine-tuning.
- Do not commit `.env` or API keys.
- Test each stage before moving to the next.
- Update this handoff after major project changes.