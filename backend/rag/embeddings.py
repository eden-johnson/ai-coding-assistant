import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from sentence_transformers import SentenceTransformer

_model = None


def get_embedding_model():
    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return _model


def create_embeddings(texts):
    model = get_embedding_model()

    return model.encode(
        texts,
        show_progress_bar=False
    )