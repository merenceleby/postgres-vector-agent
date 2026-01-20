-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create schema
CREATE SCHEMA IF NOT EXISTS rag_system;

-- Documents table with partitioning support
CREATE TABLE rag_system.documents (
    id SERIAL,
    tenant_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id, tenant_id)
) PARTITION BY LIST (tenant_id);

-- Create default partition
CREATE TABLE rag_system.documents_default PARTITION OF rag_system.documents DEFAULT;

-- Query performance tracking table
CREATE TABLE rag_system.query_metrics (
    id SERIAL PRIMARY KEY,
    query_type VARCHAR(50),
    execution_time_ms FLOAT,
    index_used BOOLEAN,
    rows_scanned INTEGER,
    query_plan JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Agent actions log
CREATE TABLE rag_system.agent_actions (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(100),
    reasoning TEXT,
    sql_executed TEXT,
    success BOOLEAN,
    impact_metrics JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes table to track created indexes
CREATE TABLE rag_system.index_registry (
    id SERIAL PRIMARY KEY,
    index_name VARCHAR(255) UNIQUE,
    table_name VARCHAR(255),
    index_type VARCHAR(50),
    created_by VARCHAR(50) DEFAULT 'agent',
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Create initial GIN index for metadata search
CREATE INDEX IF NOT EXISTS idx_documents_metadata 
ON rag_system.documents USING GIN (metadata);

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA rag_system TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA rag_system TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA rag_system TO postgres;

-- Enable pg_stat_statements
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
