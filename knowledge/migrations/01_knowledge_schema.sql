CREATE SCHEMA IF NOT EXISTS knowledge;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge.sources (
    source_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    authority VARCHAR NOT NULL,
    authority_level VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    province VARCHAR,
    source_type VARCHAR NOT NULL,
    allowed_domains JSONB NOT NULL DEFAULT '[]',
    crop_scope JSONB NOT NULL DEFAULT '[]',
    problem_scope JSONB NOT NULL DEFAULT '[]',
    language VARCHAR NOT NULL,
    retrieval_method VARCHAR NOT NULL,
    license_or_usage_notes TEXT,
    last_checked TIMESTAMP WITH TIME ZONE,
    last_successful_ingestion TIMESTAMP WITH TIME ZONE,
    content_checksum VARCHAR,
    review_status VARCHAR NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE knowledge.documents (
    document_id VARCHAR PRIMARY KEY,
    source_id VARCHAR NOT NULL REFERENCES knowledge.sources(source_id),
    title VARCHAR NOT NULL,
    source_url TEXT NOT NULL,
    retrieved_at TIMESTAMP WITH TIME ZONE NOT NULL,
    content_checksum VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    jurisdiction_country VARCHAR NOT NULL,
    jurisdiction_province VARCHAR,
    crops JSONB NOT NULL DEFAULT '[]',
    problems JSONB NOT NULL DEFAULT '[]',
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE knowledge.chunks (
    chunk_id VARCHAR PRIMARY KEY,
    document_id VARCHAR NOT NULL REFERENCES knowledge.documents(document_id),
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    tokens INTEGER NOT NULL,
    heading_hierarchy JSONB NOT NULL DEFAULT '[]',
    embedding vector(768)
);

CREATE TABLE knowledge.economic_thresholds (
    threshold_id VARCHAR PRIMARY KEY,
    crop_id VARCHAR NOT NULL,
    problem_id VARCHAR NOT NULL,
    common_name VARCHAR NOT NULL,
    scientific_name VARCHAR,
    measurement_type VARCHAR NOT NULL,
    minimum_value DOUBLE PRECISION,
    maximum_value DOUBLE PRECISION,
    unit VARCHAR NOT NULL,
    sample_unit VARCHAR,
    season VARCHAR,
    month_start INTEGER,
    month_end INTEGER,
    growth_stage VARCHAR,
    conditions JSONB NOT NULL DEFAULT '{}',
    source_id VARCHAR NOT NULL REFERENCES knowledge.sources(source_id),
    source_url TEXT NOT NULL,
    retrieved_at TIMESTAMP WITH TIME ZONE NOT NULL,
    effective_date TIMESTAMP WITH TIME ZONE,
    source_checksum VARCHAR NOT NULL,
    parser_version VARCHAR NOT NULL,
    review_status VARCHAR NOT NULL
);

CREATE TABLE knowledge.scouting_guidance (
    guidance_id VARCHAR PRIMARY KEY,
    crop_id VARCHAR NOT NULL,
    problem_id VARCHAR NOT NULL,
    sampling_unit VARCHAR NOT NULL,
    observation_method VARCHAR NOT NULL,
    frequency VARCHAR NOT NULL,
    season VARCHAR,
    distribution_guidance TEXT,
    source_id VARCHAR NOT NULL REFERENCES knowledge.sources(source_id),
    source_url TEXT NOT NULL,
    retrieved_at TIMESTAMP WITH TIME ZONE NOT NULL,
    review_status VARCHAR NOT NULL
);

CREATE TABLE knowledge.pesticide_registrations (
    registration_id VARCHAR PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    registrant VARCHAR NOT NULL,
    active_ingredients JSONB NOT NULL DEFAULT '[]',
    concentration VARCHAR,
    formulation VARCHAR,
    registered_crops JSONB NOT NULL DEFAULT '[]',
    registered_targets JSONB NOT NULL DEFAULT '[]',
    registration_status VARCHAR NOT NULL,
    source_id VARCHAR NOT NULL REFERENCES knowledge.sources(source_id),
    source_url TEXT NOT NULL,
    retrieved_at TIMESTAMP WITH TIME ZONE NOT NULL,
    checksum VARCHAR NOT NULL,
    review_status VARCHAR NOT NULL
);

CREATE TABLE knowledge.ipm_options (
    option_id VARCHAR PRIMARY KEY,
    crop_id VARCHAR NOT NULL,
    problem_id VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    description TEXT NOT NULL,
    source_id VARCHAR NOT NULL REFERENCES knowledge.sources(source_id),
    source_url TEXT NOT NULL,
    retrieved_at TIMESTAMP WITH TIME ZONE NOT NULL,
    review_status VARCHAR NOT NULL
);
