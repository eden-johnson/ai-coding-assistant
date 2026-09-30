"""
Wraps ChromaDB: stores chunk embeddings with their metadata, and lets us
search for the chunks most relevant to a question.

Each repo gets its own ChromaDB "collection" (think: a separate table),
so indexing a second repo never mixes its code into the first repo's
search results.
"""

import chromadb

# PersistentClient writes to disk (./chroma_db) so the index survives
# between runs — you don't want to re-embed the whole repo every time
# someone restarts the server. (This folder is in .gitignore already.)
client = chromadb.PersistentClient(path="./chroma_db",settings=chromadb.Settings(
        anonymized_telemetry=False
    ))


def get_collection(repo_id: str):
    """
    Gets (or creates, if it doesn't exist yet) the ChromaDB collection
    for a given repo. repo_id should be a short unique slug, e.g.
    "pypa-sampleproject", so each repo's chunks live in their own space.
    """
    return client.get_or_create_collection(name=repo_id)


def add_chunks(repo_id: str, chunks: list[dict], embeddings: list[list[float]]) -> None:
    """
    Stores chunks + their embeddings in the repo's collection.

    chunks: [{"content", "file", "language", "start_line", "end_line"}, ...]
    embeddings: matching list of vectors, same order as chunks
    """
    collection = get_collection(repo_id)

    # ChromaDB wants four parallel lists, all the same length and order:
    # - ids: a unique string per chunk (it has no idea what "unique" means for us,
    #   so we build one out of file path + line numbers)
    # - embeddings: the vectors themselves
    # - documents: the raw text (so we can show it back later without a second lookup)
    # - metadatas: everything else we want to filter/display, e.g. file + line numbers
    ids = [f"{c['file']}:{c['start_line']}-{c['end_line']}" for c in chunks]
    documents = [c["content"] for c in chunks]
    metadatas = [
        {
            "file": c["file"],
            "language": c["language"],
            "start_line": c["start_line"],
            "end_line": c["end_line"],
        }
        for c in chunks
    ]

    collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def search(repo_id: str, query_embedding: list[float], n_results: int = 5) -> list[dict]:
    """
    Finds the chunks most semantically similar to a query embedding.

    returns: [{"content", "file", "start_line", "end_line", "distance"}, ...]
    ordered from most to least relevant (smallest distance = most similar).
    """
    collection = get_collection(repo_id)

    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

    # Chroma returns everything nested one level deeper than you'd expect
    # (a list of lists — one outer list per query we sent). We only sent
    # one query, so we grab index [0] to unwrap it.
    matches = []
    for doc, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        matches.append(
            {
                "content": doc,
                "file": meta["file"],
                "start_line": meta["start_line"],
                "end_line": meta["end_line"],
                "distance": distance,
            }
        )

    return matches
