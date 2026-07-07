"""
Model evaluation utilities.

precision_at_k: holds out the most recent interaction per user (leave-one-out),
retrains-free evaluation using the already-fit collaborative model, and checks
whether the held-out item appears in the model's top-k recommendations.
This is a standard, interview-friendly offline metric for implicit-feedback
recommenders.
"""
from __future__ import annotations
import pandas as pd


def precision_at_k(collab_model, interactions_df: pd.DataFrame, k: int = 10, sample_users: int = 200) -> float:
    if interactions_df.empty:
        return 0.0

    hits, total = 0, 0
    users = interactions_df["user_id"].unique()[:sample_users]
    for user_id in users:
        user_items = set(interactions_df.loc[interactions_df.user_id == user_id, "product_id"])
        if len(user_items) < 2 or not collab_model.is_known_user(user_id):
            continue
        held_out = list(user_items)[-1]
        seen = user_items - {held_out}
        recs = collab_model.recommend_for_user(user_id, top_k=k, exclude_seen=seen)
        rec_ids = {pid for pid, _ in recs}
        hits += int(held_out in rec_ids)
        total += 1

    return hits / total if total > 0 else 0.0
