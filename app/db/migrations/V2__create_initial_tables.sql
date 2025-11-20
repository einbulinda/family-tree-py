-- ================================
-- V1__create_initial_tables.sql
-- Family Tree Application
-- For FastAPI + PostgreSQL + Alembic
-- ================================

-- ================================
-- USERS TABLE
-- ================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member', -- admin | member | viewer
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- INVITATIONS TABLE
-- ================================
CREATE TABLE invitations (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    invited_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    is_accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- INDIVIDUALS TABLE
-- Represents people in a family tree
-- ================================
CREATE TABLE individuals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    last_name VARCHAR(255),
    gender VARCHAR(20) CHECK (gender IN ('male', 'female')),
    birth_date DATE,
    death_date DATE,
    is_alive BOOLEAN DEFAULT TRUE,
    bio TEXT,
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster search
CREATE INDEX idx_individuals_user ON individuals(user_id);

-- ================================
-- RELATIONSHIPS TABLE
-- Parent-child, spouse, sibling
-- ================================
CREATE TABLE relationships (
    id SERIAL PRIMARY KEY,
    individual_id INTEGER NOT NULL REFERENCES individuals(id) ON DELETE CASCADE,
    related_individual_id INTEGER NOT NULL REFERENCES individuals(id) ON DELETE CASCADE,
    relationship_type VARCHAR(20) NOT NULL CHECK (
        relationship_type IN ('parent', 'child', 'spouse') -- sibling relationship is derived from person with same parents
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prevent duplicate relationship entries
CREATE UNIQUE INDEX unique_relationship_pair
ON relationships(individual_id, related_individual_id, relationship_type);

-- Avoid self-relationship (a person can't relate to themselves)
ALTER TABLE relationships
ADD CONSTRAINT no_self_relationship
CHECK (individual_id <> related_individual_id);

-- ================================
-- OPTIONAL FUTURE TABLES
-- events, documents, photos, lineage logs
-- ================================
