"""
Local embedding utilities.

Uses sentence-transformers instead of the OpenAI embeddings API,
so embedding code chunks and questions does not require API credits.
"""

from sentence_transformers import SentenceTransformer


# A small, fast model suitable for an MVP.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

model = SentenceTransformer(EMBEDDING_MODEL)


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple text strings into embedding vectors.

    The returned vectors are in the same order as the input texts.
    """

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return embeddings.tolist()


def get_embedding(text: str) -> list[float]:
    """
    Convert one text string into a single embedding vector.
    """

    return get_embeddings([text])[0]