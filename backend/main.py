from fastapi import FastAPI
from pydantic import BaseModel

from ingestion.github import clone_repository, cleanup_repository
from ingestion.file_loader import scan_repository
from ingestion.chunker import chunk_files
from rag.embeddings import get_embeddings, get_embedding
from rag.vector_store import add_chunks, search
from rag.llm import generate_answer

app = FastAPI(title="AI Codebase Assistant")


def repo_id_from_url(repo_url: str) -> str:
    owner_repo = repo_url.rstrip("/").split("github.com/")[-1]
    return owner_repo.replace("/", "-")


class IndexRequest(BaseModel):
    repo_url: str


class AskRequest(BaseModel):
    repo_url: str
    question: str


@app.post("/index")
def index_repo(req: IndexRequest):
    repo_id = repo_id_from_url(req.repo_url)
    local_path = clone_repository(req.repo_url)

    try:
        files = scan_repository(local_path)
        chunks = chunk_files(files)

        chunk_texts = [c["content"] for c in chunks]
        chunk_embeddings = get_embeddings(chunk_texts)

        add_chunks(repo_id, chunks, chunk_embeddings)

        return {
            "repo_id": repo_id,
            "files_scanned": len(files),
            "chunks_stored": len(chunks),
        }
    finally:
        cleanup_repository(local_path)


@app.post("/ask")
def ask_question(req: AskRequest):
    repo_id = repo_id_from_url(req.repo_url)

    question_embedding = get_embedding(req.question)
    results = search(repo_id, question_embedding, n_results=3)

    answer = generate_answer(req.question, results)

    return {
        "answer": answer,
        "sources": [
            {"file": r["file"], "start_line": r["start_line"], "end_line": r["end_line"]}
            for r in results
        ],
    }