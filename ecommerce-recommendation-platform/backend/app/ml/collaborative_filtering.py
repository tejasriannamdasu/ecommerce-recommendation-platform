"""
Collaborative Filtering Recommender (Matrix Factorization)
-------------------------------------------------------------
Builds a sparse user-item interaction matrix (weighted blend of
views, clicks, purchases, and explicit ratings) and factorizes it
with Non-Negative Matrix Factorization (NMF) into latent user and
item embeddings. Recommendation = dot product of a user's latent
vector with every item's latent vector, i.e. "users who behaved
like you also engaged with these items."

NMF is used (over pure SVD) because interaction weights/ratings are
non-negative and NMF's factors are more interpretable (each latent
dimension can be read as a soft "taste cluster").
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import NMF
import joblib
import os


class CollaborativeFilteringRecommender:
    def __init__(self, n_components: int = 20, max_iter: int = 200, random_state: int = 42):
        self.n_components = n_components
        self.max_iter = max_iter
        self.random_state = random_state
        self.model: NMF | None = None
        self.user_factors: np.ndarray | None = None
        self.item_factors: np.ndarray | None = None
        self.user_ids: list[int] = []
        self.product_ids: list[int] = []
        self._user_to_row: dict[int, int] = {}
        self._item_to_col: dict[int, int] = {}

    def fit(self, interactions_df: pd.DataFrame) -> "CollaborativeFilteringRecommender":
        """
        interactions_df columns required: user_id, product_id, weight
        (weight = combined implicit/explicit signal, e.g. view=1, click=2,
        purchase=5, rating scaled 1-5)
        """
        self.user_ids = sorted(interactions_df["user_id"].unique().tolist())
        self.product_ids = sorted(interactions_df["product_id"].unique().tolist())
        self._user_to_row = {u: i for i, u in enumerate(self.user_ids)}
        self._item_to_col = {p: i for i, p in enumerate(self.product_ids)}

        rows = interactions_df["user_id"].map(self._user_to_row)
        cols = interactions_df["product_id"].map(self._item_to_col)
        vals = interactions_df["weight"].astype(float)

        matrix = csr_matrix(
            (vals, (rows, cols)),
            shape=(len(self.user_ids), len(self.product_ids)),
        )

        n_components = min(self.n_components, min(matrix.shape) - 1) if min(matrix.shape) > 1 else 1
        n_components = max(n_components, 1)

        self.model = NMF(
            n_components=n_components,
            init="nndsvda",
            max_iter=self.max_iter,
            random_state=self.random_state,
        )
        self.user_factors = self.model.fit_transform(matrix)
        self.item_factors = self.model.components_.T  # (n_items, n_components)
        return self

    def recommend_for_user(self, user_id: int, top_k: int = 10, exclude_seen: set[int] | None = None) -> list[tuple[int, float]]:
        if user_id not in self._user_to_row or self.item_factors is None:
            return []
        u_row = self._user_to_row[user_id]
        scores = self.item_factors @ self.user_factors[u_row]
        ranked = np.argsort(-scores)
        exclude_seen = exclude_seen or set()
        results = []
        for idx in ranked:
            pid = self.product_ids[idx]
            if pid in exclude_seen:
                continue
            results.append((pid, float(scores[idx])))
            if len(results) >= top_k:
                break
        return results

    def similar_items(self, product_id: int, top_k: int = 10) -> list[tuple[int, float]]:
        """Item-item similarity in latent space — used for 'similar products'."""
        if product_id not in self._item_to_col or self.item_factors is None:
            return []
        col = self._item_to_col[product_id]
        target = self.item_factors[col]
        norms = np.linalg.norm(self.item_factors, axis=1) * np.linalg.norm(target) + 1e-9
        sims = (self.item_factors @ target) / norms
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

    def is_known_user(self, user_id: int) -> bool:
        return user_id in self._user_to_row

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "user_factors": self.user_factors,
                "item_factors": self.item_factors,
                "user_ids": self.user_ids,
                "product_ids": self.product_ids,
            },
            os.path.join(path, "collaborative.joblib"),
        )

    @classmethod
    def load(cls, path: str) -> "CollaborativeFilteringRecommender":
        data = joblib.load(os.path.join(path, "collaborative.joblib"))
        obj = cls()
        obj.model = data["model"]
        obj.user_factors = data["user_factors"]
        obj.item_factors = data["item_factors"]
        obj.user_ids = data["user_ids"]
        obj.product_ids = data["product_ids"]
        obj._user_to_row = {u: i for i, u in enumerate(obj.user_ids)}
        obj._item_to_col = {p: i for i, p in enumerate(obj.product_ids)}
        return obj
