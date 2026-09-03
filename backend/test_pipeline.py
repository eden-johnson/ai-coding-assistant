"""
End-to-end test of Stages 1-5: clone a repo, chunk it, embed the chunks
with OpenAI, store them in ChromaDB, then search with a real question.

Run: python test_pipeline.py https://github.com/user/project "your question"
"""

import sys

from ingestion.github import clone_repository, cleanup_repository
from ingestion.file_loader import scan_repository
from ingestion.chunker import chunk_files
from rag.embeddings import get_embeddings, get_embedding
from rag.vector_store import add_chunks, search


def repo_id_from_url(repo_url: str) -> str:
    """
    Turns a GitHub URL into a short, safe collection name.
    e.g. "https://github.com/pypa/sampleproject" -> "pypa-sampleproject"
    ChromaDB collection names can't contain slashes, so we can't just use
    the URL or "owner/repo" directly.
    """
    owner_repo = repo_url.rstrip("/").split("github.com/")[-1]
    return owner_repo.replace("/", "-")


def main(repo_url: str, question: str) -> None:
    repo_id = repo_id_from_url(repo_url)

    print(f"Cloning {repo_url} ...")
    local_path = clone_repository(repo_url)

    try:
        print("Scanning + chunking ...")
        files = scan_repository(local_path)
        chunks = chunk_files(files)
        print(f"{len(files)} files -> {len(chunks)} chunks\n")

        print("Embedding chunks ...")
        chunk_texts = [c["content"] for c in chunks]
        chunk_embeddings = get_embeddings(chunk_texts)

        print("Storing in ChromaDB ...")
        add_chunks(repo_id, chunks, chunk_embeddings)
        print(f"Stored under collection '{repo_id}'\n")

        print(f"Question: {question}")
        question_embedding = get_embedding(question)
        results = search(repo_id, question_embedding, n_results=3)

        print("\nTop matching chunks:")
        for r in results:
            print(f"  📄 {r['file']}  lines {r['start_line']}-{r['end_line']}  (distance {r['distance']:.4f})")

    finally:
        cleanup_repository(local_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python test_pipeline.py <github_repo_url> "<question>"')
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
