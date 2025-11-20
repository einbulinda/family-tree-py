-- ===============================================
--  V1__create_initial_tables.sql
--  Initial database schema for Family Tree App
--  Using PostgreSQL + FastAPI + SQLAlchemy
-- ===============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-------------------------------------------------
-- USERS TABLE
-------------------------------------------------
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',              -- 'admin', 'member'
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-------------------------------------------------
-- INVITATIONS TABLE
-------------------------------------------------
CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    invited_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-------------------------------------------------
-- INDIVIDUALS TABLE (PERSON PROFILES)
-------------------------------------------------
CREATE TABLE individuals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    gender VARCHAR(20),                            -- 'male', 'female', 'other'
    birth_date DATE,
    death_date DATE,
    is_alive BOOLEAN DEFAULT TRUE,
    bio TEXT,
    photo_url TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_individuals_name ON individuals(first_name, last_name);

-------------------------------------------------
-- RELATIONSHIPS TABLE
-------------------------------------------------
CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
    related_individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,      -- parent, child, spouse
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Prevent duplicate relationships
    UNIQUE (individual_id, related_individual_id, relationship_type)
);

-- Index for faster tree traversal queries
CREATE INDEX idx_rel_individual ON relationships(individual_id);
CREATE INDEX idx_rel_related_individual ON relationships(related_individual_id);

-------------------------------------------------
-- FAMILY GROUP TABLE (optional, future use)
-- Allows grouping by household, lineage, clans, etc.
-------------------------------------------------
CREATE TABLE family_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE family_group_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES family_groups(id) ON DELETE CASCADE,
    individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE
);

-------------------------------------------------
-- LOG TABLE (Optional, for auditing)
-------------------------------------------------
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
