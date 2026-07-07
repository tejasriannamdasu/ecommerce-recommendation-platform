# Architecture

## Data flow

```
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │  (Vite + Tailwind)  │
                    └──────────┬───────────┘
                               │ HTTPS / JSON (axios, JWT bearer)
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    │  (routers + auth)   │
                    └──────────┬───────────┘
                 ┌─────────────┼──────────────┐
                 ▼             ▼              ▼
         ┌───────────┐  ┌────────────┐  ┌───────────────┐
         │ PostgreSQL │  │   Redis    │  │  ML Registry   │
         │ (catalog,  │  │ (caching,  │  │ (in-memory,    │
         │ users,     │  │ rate limit)│  │ loaded once    │
         │ orders,    │  └────────────┘  │ at startup)    │
         │ interactions)                 └───────┬────────┘
         └───────────┘                            │
                                    ┌──────────────┼──────────────┐
                                    ▼              ▼              ▼
                            ┌────────────┐ ┌──────────────┐ ┌───────────┐
                            │ Content-   │ │Collaborative │ │ Semantic  │
                            │ Based      │ │ Filtering    │ │ Search    │
                            │ (TF-IDF)   │ │ (NMF)        │ │(SBERT +   │
                            └─────┬──────┘ └──────┬───────┘ │ FAISS)    │
                                  │               │          └───────────┘
                                  └───────┬───────┘
                                          ▼
                                  ┌───────────────┐
                                  │ Hybrid Ranker │
                                  │ (weighted     │
                                  │ blend + cold- │
                                  │ start logic)  │
                                  └───────────────┘
```

## Why these choices

**TF-IDF for content-based, not embeddings, as the primary signal.**
TF-IDF is fast to retrain on every catalog change, fully explainable
(shared vocabulary = shared recommendation reason), and — critically —
gives a brand-new product a meaningful vector from day one with zero
interaction history. This is what actually solves item cold-start.

**NMF for collaborative filtering, not SVD.**
Interaction weights (views/clicks/purchases/ratings) are inherently
non-negative, and NMF's factors are more interpretable as soft "taste
clusters" than SVD's signed components — useful when defending the
model's behavior in an interview.

**Sentence-Transformers + FAISS for semantic search, with a TF-IDF fallback.**
Dense embeddings capture meaning past exact keyword overlap ("wireless
headphones for gaming" → "Bluetooth Gaming Headset"). The engine
auto-detects whether the transformer model/weights are reachable and
falls back to TF-IDF cosine similarity otherwise, so the API never
breaks in an offline/sandboxed environment.

**Redis caching, not always-live computation.**
Recommendation generation involves a matrix multiply and, in the
semantic path, a model forward-pass. Caching per-user results for a
short TTL (5-10 min) avoids recomputing on every page refresh while
keeping recommendations reasonably fresh.

**Offline training pipeline, decoupled from the live API.**
`train_pipeline.py` runs as a standalone job (cron / CI pipeline in
production) that reads from Postgres, trains all three models, and
persists them to disk. The API only ever *loads* pre-trained models at
startup — this keeps request latency low and mirrors how recommendation
systems are actually run in production (offline batch training +
online serving).

## Cold-start handling

| Scenario | Strategy |
|---|---|
| New user, no interactions | Trending / popularity-ranked products |
| New product, no interactions | Content-based similarity only (TF-IDF still works from text alone) |
| Established user + product | Weighted hybrid blend (content + collaborative) |
| Anonymous (not logged in) | Trending endpoint (no JWT required) |
