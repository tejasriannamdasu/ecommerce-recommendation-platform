# Resume Bullet Points

## Project title
**AI-Powered E-Commerce Recommendation Platform** | Python, FastAPI, React, PostgreSQL, Scikit-learn, FAISS, Docker

## Two-line summary
> Built a full-stack AI-powered e-commerce recommendation platform (FastAPI, React, PostgreSQL) with a hybrid ML engine — content-based filtering, collaborative filtering (NMF), and semantic vector search (Sentence-Transformers + FAISS) — delivering explainable, cold-start-aware personalized recommendations.
> Engineered secure JWT-authenticated APIs, a normalized relational schema, Redis caching, an offline ML training/evaluation pipeline, and an admin analytics dashboard, fully containerized with Docker Compose for one-command deployment.

## Full bullet list
- Architected and built a full-stack recommendation platform (FastAPI + React + PostgreSQL) serving personalized product recommendations via a hybrid ML pipeline combining content-based filtering, collaborative filtering, and semantic search.
- Implemented a content-based recommender using TF-IDF vectorization and cosine similarity over product titles, descriptions, and categories to power "similar product" suggestions and cold-start recommendations for new items.
- Built a collaborative filtering engine using Non-Negative Matrix Factorization (NMF) on a weighted user-item interaction matrix (views, clicks, purchases, ratings), with a custom offline precision@k evaluation harness.
- Designed a hybrid ranking layer that blends content-based and collaborative signals with configurable weights, automatically falling back to popularity-based recommendations for cold-start users.
- Integrated semantic (vector) search using Sentence-Transformers embeddings and a FAISS similarity index for natural-language product search.
- Designed a normalized relational schema (7+ tables) with proper foreign keys and indexing.
- Built secure REST APIs with JWT authentication, role-based access control, and Redis-backed caching + rate limiting.
- Developed an end-to-end ML training pipeline (collection → cleaning → feature engineering → training → evaluation → persistence) as a standalone CLI job.
- Containerized the full stack with Docker Compose for one-command local deployment.
- Built an admin analytics dashboard surfacing most-viewed/purchased products, top categories, and user activity via aggregated SQL.
- Added an explainable-AI feature ("why this was recommended") to make the recommendation logic transparent and interview-defensible.
