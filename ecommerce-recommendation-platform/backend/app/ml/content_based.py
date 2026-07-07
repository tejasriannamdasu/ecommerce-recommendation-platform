"""
Content-Based Recommender
--------------------------
Builds a TF-IDF representation of each product from its title,
description, category and tags, then recommends products whose
text vectors are closest (cosine similarity) to a target product
or to a synthesized "user profile" vector (average of items the
user has interacted with).

Why TF-IDF here: it's fast to train/refresh, needs no GPU, is fully
explainable (we can point to shared vocabulary/tags), and is the
right tool for a cold-start item (a brand-new product with zero
interactions still gets a meaningful vector from its text alone).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os


class ContentBasedRecommender:
    def __init__(self, max_features: int = 20000):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self.tfidf_matrix = None
        self.product_ids: list[int] = []
        self._id_to_row: dict[int, int] = {}

    @staticmethod
    def _build_corpus(df: pd.DataFrame) -> pd.Series:
        # Weight title higher by repeating it — cheap way to bias TF-IDF
        # towards the most informative field without a custom vectorizer.
        return (
            (df["title"].fillna("") + " ") * 2
            + df["category"].fillna("") + " "
            + df["tags"].fillna("") + " "
            + df["description"].fillna("")
        )

    def fit(self, products_df: pd.DataFrame) -> "ContentBasedRecommender":
        """
        products_df columns required: id, title, description, category, tags
        """
        corpus = self._build_corpus(products_df)
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.product_ids = products_df["id"].tolist()
        self._id_to_row = {pid: i for i, pid in enumerate(self.product_ids)}
        return self

    def similar_to_product(self, product_id: int, top_k: int = 10) -> list[tuple[int, float]]:
        if product_id not in self._id_to_row:
            return []
        row = self._id_to_row[product_id]
        sims = cosine_similarity(self.tfidf_matrix[row], self.tfidf_matrix).flatten()
        ranked = np.argsort(-sims)
        results = []
        for idx in ranked:
            pid = self.product_ids[idx]
            if pid == product_id:
                continue
            results.append((pid, float(sims[idx])))
            if len(results) >= top_k:
                break
        return results

    def recommend_for_profile(self, product_ids_liked: list[int], top_k: int = 10) -> list[tuple[int, float]]:
        """Average the vectors of products a user has engaged with to build
        an implicit taste profile, then rank the full catalog against it."""
        rows = [self._id_to_row[pid] for pid in product_ids_liked if pid in self._id_to_row]
        if not rows:
            return []
        profile_vec = self.tfidf_matrix[rows].mean(axis=0)
        profile_vec = np.asarray(profile_vec)
        sims = cosine_similarity(profile_vec, self.tfidf_matrix).flatten()
        ranked = np.argsort(-sims)
        results = []
        seen = set(product_ids_liked)
        for idx in ranked:
            pid = self.product_ids[idx]
            if pid in seen:
                continue
            results.append((pid, float(sims[idx])))
            if len(results) >= top_k:
                break
        return results

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        joblib.dump(
            {
                "vectorizer": self.vectorizer,
                "tfidf_matrix": self.tfidf_matrix,
                "product_ids": self.product_ids,
            },
            os.path.join(path, "content_based.joblib"),
        )

    @classmethod
    def load(cls, path: str) -> "ContentBasedRecommender":
        data = joblib.load(os.path.join(path, "content_based.joblib"))
        obj = cls()
        obj.vectorizer = data["vectorizer"]
        obj.tfidf_matrix = data["tfidf_matrix"]
        obj.product_ids = data["product_ids"]
        obj._id_to_row = {pid: i for i, pid in enumerate(obj.product_ids)}
        return obj
