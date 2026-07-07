# Signal — AI-Powered E-Commerce Recommendation Platform

A full-stack recommendation platform combining **content-based filtering**,
**collaborative filtering (matrix factorization)**, and **semantic vector
search** into a single hybrid, explainable recommendation engine — built with
production patterns (JWT auth, RBAC, Redis caching, rate limiting, Docker)
rather than a notebook-only ML demo.

> Built to be discussed confidently in software engineering and ML
> interviews: every model choice below is paired with a rationale in
> [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Features

**User-facing**
- Registration/login (JWT), product search & filtering, product detail pages
- Personalized recommendations, similar-product suggestions, recently viewed, wishlist, profile

**AI / ML**
- Content-based recommendations (TF-IDF + cosine similarity)
- Collaborative filtering (Non-Negative Matrix Factorization on weighted interactions)
- Hybrid ranking that blends both, with automatic cold-start fallback to trending items
- Semantic search (Sentence-Transformers + FAISS, with a TF-IDF fallback if the
  transformer model can't be downloaded — e.g. no internet)
- Recommendation explanations ("why this was recommended")
- Search autocomplete

**Platform**
- Admin analytics dashboard (most viewed/purchased, top categories, user activity)
- Redis caching + API rate limiting
- Role-based access control (customer / admin)
- Dockerized end-to-end (`docker-compose up`)

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React (Vite), Tailwind CSS |
| Database | PostgreSQL |
| ML | Scikit-learn, Pandas, NumPy |
| Semantic search | Sentence-Transformers, FAISS |
| Caching | Redis |
| Deployment | Docker, Docker Compose |

## Folder structure

```
backend/
  app/
    models/       SQLAlchemy ORM models (users, products, interactions, orders...)
    schemas/      Pydantic request/response schemas
    routers/      FastAPI route handlers (auth, products, recommendations, analytics, wishlist)
    auth/         JWT creation/verification, password hashing, RBAC dependency
    ml/           Content-based, collaborative filtering, hybrid, semantic search, training pipeline
    utils/        Redis cache wrapper, rate limiter
    main.py       App entrypoint — wires routers + loads ML models on startup
    config.py     Centralized settings (env-driven)
  scripts/        generate_dataset.py, seed_db.py, train_models.py
  Dockerfile
database/
  schema.sql      Documented SQL schema (SQLAlchemy creates the same tables at runtime)
  seed_csv/       Generated synthetic catalog + interactions (or swap in a real dataset)
frontend/
  src/
    pages/        Home, ProductDetail, Login, Register, Profile, Wishlist, AdminDashboard, SearchResults
    components/   Navbar, ProductCard, RecommendationRail
    api/          Axios client + auth context
  Dockerfile
ml_models/        Trained model artifacts land here (.joblib, FAISS index) — gitignored
docs/
  ARCHITECTURE.md, API_DOCUMENTATION.md, RESUME_BULLETS.md
docker-compose.yml
```

## Quick start

### Option A — Docker (recommended)

```bash
cp .env.example .env
docker-compose up --build
```

Then, in a separate terminal, seed the database and train the models:

```bash
docker-compose exec backend python scripts/generate_dataset.py
docker-compose exec backend python scripts/seed_db.py
docker-compose exec backend python scripts/train_models.py
```

- API: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173
- Demo accounts: `admin@example.com` / `Admin@123`, `user1@example.com` / `Password@123`

### Option B — Local dev (no Docker)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Start Postgres & Redis locally, or point DATABASE_URL/REDIS_URL at hosted instances
python scripts/generate_dataset.py
python scripts/seed_db.py
python scripts/train_models.py
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Using a real dataset (Amazon Reviews / Retailrocket)

The pipeline is dataset-agnostic — `generate_dataset.py` just needs to
produce three CSVs: `products.csv` (id, title, description, category, tags,
price, brand, image_url), `interactions.csv` (user_id, product_id,
interaction_type), and `ratings.csv` (user_id, product_id, score). To train
on a real dataset instead of the synthetic generator:

1. Download the [Amazon Product Reviews](https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/)
   or [Retailrocket](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset) dataset.
2. Map its columns to the three CSV schemas above (a short pandas script —
   Retailrocket's `events.csv` already maps almost 1:1 to `interactions.csv`).
3. Drop the CSVs into `database/seed_csv/` and run `seed_db.py` + `train_models.py` as usual.

This matters for resume/interview credibility — recruiters notice when a
recommender is trained on realistic, messy, real-world interaction data
rather than a toy dataset.

## ML pipeline

`backend/app/ml/train_pipeline.py` runs offline (not on the request path):

1. **Data collection** — pulls products/interactions/ratings from PostgreSQL
2. **Data cleaning** — dedupes, aggregates repeated signals, clips outlier weights
3. **Feature engineering** — builds the TF-IDF text corpus and the weighted interaction matrix
4. **Model training** — fits content-based (TF-IDF), collaborative (NMF), and semantic (SBERT+FAISS) models
5. **Model evaluation** — precision@10 on a held-out interaction split
6. **Persistence** — saves all three models to `ml_models/`; the API loads them once at startup

Re-run it any time the catalog or interaction data changes:
```bash
python scripts/train_models.py
```

## API documentation

See [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) for the full
endpoint reference, or the live interactive docs at `/docs` once running.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the data-flow diagram
and the reasoning behind each model/technology choice.

## Future enhancements

- Deep learning-based recommenders (e.g. two-tower neural retrieval, sequence models for session-based recommendations)
- A/B testing framework to compare recommendation strategies in production
- Real-time streaming interaction ingestion (Kafka) instead of batch retraining
- Alembic migrations instead of `create_all` for schema evolution
- CI/CD pipeline (GitHub Actions) running tests + the training pipeline on push

## Resume impact

See [`docs/RESUME_BULLETS.md`](docs/RESUME_BULLETS.md) for ready-to-use resume bullet points.
