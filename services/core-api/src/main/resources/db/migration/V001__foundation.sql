CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Identity
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    sub VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_name VARCHAR(255),
    fcm_token VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Farms
CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location_lat DOUBLE PRECISION,
    location_lng DOUBLE PRECISION,
    area DOUBLE PRECISION,
    area_unit VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    version BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS farm_memberships (
    id UUID PRIMARY KEY,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(farm_id, user_id)
);

-- Fields
CREATE TABLE IF NOT EXISTS fields (
    id UUID PRIMARY KEY,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location_lat DOUBLE PRECISION,
    location_lng DOUBLE PRECISION,
    area DOUBLE PRECISION,
    area_unit VARCHAR(50),
    active_crop_cycle_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    version BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS field_boundaries (
    id UUID PRIMARY KEY,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    boundary_polygon JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Crop Cycles
CREATE TABLE IF NOT EXISTS crop_cycles (
    id UUID PRIMARY KEY,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    crop_id VARCHAR(255) NOT NULL,
    variety VARCHAR(255),
    sowing_date DATE,
    expected_harvest_date DATE,
    actual_harvest_date DATE,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    version BIGINT NOT NULL DEFAULT 0
);

ALTER TABLE fields ADD CONSTRAINT fk_active_crop_cycle FOREIGN KEY (active_crop_cycle_id) REFERENCES crop_cycles(id) ON DELETE SET NULL;

-- Storage
CREATE TABLE IF NOT EXISTS storage_objects (
    id UUID PRIMARY KEY,
    object_key VARCHAR(255) UNIQUE NOT NULL,
    content_type VARCHAR(100),
    size_bytes BIGINT,
    sha_256 VARCHAR(255),
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    context VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexes
CREATE INDEX idx_farm_memberships_user_id ON farm_memberships(user_id);
CREATE INDEX idx_fields_farm_id ON fields(farm_id);
CREATE INDEX idx_crop_cycles_field_status ON crop_cycles(field_id, status);
