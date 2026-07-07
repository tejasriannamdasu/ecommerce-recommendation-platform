"""
Semantic Search Engine
------------------------
Encodes every product's text into a dense embedding using a
Sentence-Transformers model, indexes those embeddings in a FAISS
flat inner-product index (cosine similarity via L2-normalized
vectors), and at query time encodes the free-text search string
into the same space to retrieve semantically similar products —
so "wireless headphones for gaming" matches a listing titled
"Bluetooth Gaming Headset" even without exact keyword overlap.

Graceful degradation: if sentence-transformers/faiss aren't
installed or the model can't be downloaded (e.g. no internet in a
sandboxed environment), this falls back to the TF-IDF vectorizer
from the content-based recommender so the API keeps working.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import joblib

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    _SEMANTIC_LIBS_AVAILABLE = True
except Exception:
    _SEMANTIC_LIBS_AVAILABLE = False


class SemanticSearchEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.index = None
        self.product_ids: list[int] = []
        self._fallback_vectorizer = None
        self._fallback_matrix = None
        self.mode = "uninitialized"

    def fit(self, products_df: pd.DataFrame):
        """products_df columns required: id, title, description, category, tags"""
        texts = (
            products_df["title"].fillna("") + ". " +
            products_df["description"].fillna("") + ". Category: " +
            products_df["category"].fillna("") + ". Tags: " +
            products_df["tags"].fillna("")
        ).tolist()
        self.product_ids = products_df["id"].tolist()

        if _SEMANTIC_LIBS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
                embeddings = self.model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
                embeddings = np.asarray(embeddings, dtype="float32")
                self.index = faiss.IndexFlatIP(embeddings.shape[1])
                self.index.add(embeddings)
                self.mode = "sentence-transformers+faiss"
                return self
            except Exception:
                pass  # fall through to TF-IDF fallback (e.g. no network for model weights)

        # --- Fallback: TF-IDF + cosine similarity, same public interface ---
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._fallback_vectorizer = TfidfVectorizer(max_features=20000, stop_words="english")
        self._fallback_matrix = self._fallback_vectorizer.fit_transform(texts)
        self.mode = "tfidf-fallback"
        return self

    def search(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        if self.mode == "sentence-transformers+faiss":
            q_vec = self.model.encode([query], normalize_embeddings=True).astype("float32")
            scores, indices = self.index.search(q_vec, top_k)
            return [
                (self.product_ids[idx], float(score))
                for idx, score in zip(indices[0], scores[0]) if idx != -1
            ]
        elif self.mode == "tfidf-fallback":
            from sklearn.metrics.pairwise import cosine_similarity
            q_vec = self._fallback_vectorizer.transform([query])
            sims = cosine_similarity(q_vec, self._fallback_matrix).flatten()
            ranked = np.argsort(-sims)[:top_k]
            return [(self.product_ids[i], float(sims[i])) for i in ranked]
        else:
            raise RuntimeError("SemanticSearchEngine not fitted yet")

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        if self.mode == "sentence-transformers+faiss":
            faiss.write_index(self.index, os.path.join(path, "faiss.index"))
            joblib.dump(
                {"product_ids": self.product_ids, "model_name": self.model_name, "mode": self.mode},
                os.path.join(path, "semantic_meta.joblib"),
            )
        else:
            joblib.dump(
                {
                    "vectorizer": self._fallback_vectorizer,
                    "matrix": self._fallback_matrix,
                    "product_ids": self.product_ids,
                    "mode": self.mode,
                },
                os.path.join(path, "semantic_fallback.joblib"),
            )

    @classmethod
    def load(cls, path: str) -> "SemanticSearchEngine":
        obj = cls()
        faiss_path = os.path.join(path, "faiss.index")
        if _SEMANTIC_LIBS_AVAILABLE and os.path.exists(faiss_path):
            obj.index = faiss.read_index(faiss_path)
            meta = joblib.load(os.path.join(path, "semantic_meta.joblib"))
            obj.product_ids = meta["product_ids"]
            obj.model_name = meta["model_name"]
            obj.model = SentenceTransformer(obj.model_name)
            obj.mode = "sentence-transformers+faiss"
        else:
            data = joblib.load(os.path.join(path, "semantic_fallback.joblib"))
            obj._fallback_vectorizer = data["vectorizer"]
            obj._fallback_matrix = data["matrix"]
            obj.product_ids = data["product_ids"]
            obj.mode = "tfidf-fallback"
        return obj
