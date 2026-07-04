-- ============================================================
-- Database Initialisation Script
-- Run once by Docker Compose on first container start.
-- ============================================================

-- Create the application database (already created by POSTGRES_DB env var,
-- but this script can be extended with schema grants, extensions, etc.)

-- Enable the pgcrypto extension for UUID generation in PostgreSQL
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable the pg_trgm extension for trigram-based text search
-- (used by the future knowledge base for fuzzy log matching)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enable the vector extension (pgvector) if installed
-- Uncomment when Knowledge Base sprint begins:
-- CREATE EXTENSION IF NOT EXISTS "vector";

-- Audit comment
SELECT 'Database initialised successfully at ' || NOW() AS init_status;
