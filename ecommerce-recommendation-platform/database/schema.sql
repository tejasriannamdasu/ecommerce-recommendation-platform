-- ============================================================
-- AI-Powered E-Commerce Recommendation Platform — PostgreSQL Schema
-- Note: In the running app, SQLAlchemy (see backend/app/models/*)
-- creates these same tables automatically. This file is provided
-- for documentation, manual setup, and interview walkthroughs.
-- ============================================================

CREATE TYPE user_role AS ENUM ('customer', 'admin');
CREATE TYPE interaction_type AS ENUM ('view', 'click', 'purchase', 'wishlist');

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    username        VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'customer',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(150) UNIQUE NOT NULL,
    parent_id   INTEGER REFERENCES categories(id)
);

CREATE TABLE products (
    id                SERIAL PRIMARY KEY,
    title             VARCHAR(500) NOT NULL,
    description       TEXT,
    tags              VARCHAR(500),
    price             FLOAT NOT NULL DEFAULT 0,
    category_id       INTEGER REFERENCES categories(id),
    brand             VARCHAR(150),
    image_url         VARCHAR(500),
    avg_rating        FLOAT DEFAULT 0,
    num_ratings       INTEGER DEFAULT 0,
    popularity_score  FLOAT DEFAULT 0,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_products_title ON products USING GIN (to_tsvector('english', title));
CREATE INDEX idx_products_category ON products (category_id);
CREATE INDEX idx_products_popularity ON products (popularity_score DESC);

CREATE TABLE user_interactions (
    id                 SERIAL PRIMARY KEY,
    user_id            INTEGER NOT NULL REFERENCES users(id),
    product_id         INTEGER NOT NULL REFERENCES products(id),
    interaction_type   interaction_type NOT NULL,
    weight             FLOAT DEFAULT 1.0,
    created_at         TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_interactions_user ON user_interactions (user_id);
CREATE INDEX idx_interactions_product ON user_interactions (product_id);
CREATE INDEX idx_interactions_type ON user_interactions (interaction_type);

CREATE TABLE ratings (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    score       FLOAT NOT NULL CHECK (score >= 1 AND score <= 5),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, product_id)
);

CREATE TABLE orders (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    status        VARCHAR(50) DEFAULT 'completed',
    total_amount  FLOAT DEFAULT 0,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER DEFAULT 1,
    unit_price  FLOAT DEFAULT 0
);

CREATE TABLE wishlist (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, product_id)
);

-- ============================================================
-- Entity relationships:
--   users (1) ----< user_interactions >---- (1) products
--   users (1) ----< ratings >---- (1) products
--   users (1) ----< orders (1) ----< order_items >---- (1) products
--   users (1) ----< wishlist >---- (1) products
--   categories (1) ----< products
--   categories (1) ----< categories   (self-referencing, for subcategories)
-- ============================================================
