ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(16) NOT NULL DEFAULT 'en';
ALTER TABLE users ALTER COLUMN sub DROP NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_normalized ON users (LOWER(email)) WHERE email IS NOT NULL;

CREATE TABLE crops (
    id UUID PRIMARY KEY, slug VARCHAR(64) UNIQUE NOT NULL, name VARCHAR(120) NOT NULL,
    supported BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE pests (
    id UUID PRIMARY KEY, slug VARCHAR(96) UNIQUE NOT NULL, common_name VARCHAR(160) NOT NULL,
    scientific_name VARCHAR(200) NOT NULL, description TEXT NOT NULL, supported BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE crop_pests (
    crop_id UUID NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    pest_id UUID NOT NULL REFERENCES pests(id) ON DELETE CASCADE,
    PRIMARY KEY (crop_id, pest_id)
);
CREATE TABLE pest_guidance (
    pest_id UUID PRIMARY KEY REFERENCES pests(id) ON DELETE CASCADE,
    damage_description TEXT NOT NULL, prevention TEXT NOT NULL, basic_management TEXT NOT NULL,
    expert_advice_note TEXT NOT NULL, source_name VARCHAR(255) NOT NULL, source_url TEXT NOT NULL,
    last_verified_at DATE NOT NULL
);
CREATE TABLE scans (
    id UUID PRIMARY KEY, user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    crop_id UUID NOT NULL REFERENCES crops(id), image_key VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL CHECK (status IN ('IDENTIFIED', 'UNKNOWN', 'REJECTED_IMAGE', 'FAILED')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TABLE scan_predictions (
    scan_id UUID PRIMARY KEY REFERENCES scans(id) ON DELETE CASCADE, pest_id UUID REFERENCES pests(id),
    confidence DECIMAL(7, 6), bbox_x DECIMAL(8, 7), bbox_y DECIMAL(8, 7),
    bbox_width DECIMAL(8, 7), bbox_height DECIMAL(8, 7), model_id VARCHAR(120),
    model_version VARCHAR(80), dataset_version VARCHAR(120), result_type VARCHAR(32) NOT NULL, reason VARCHAR(64)
);
CREATE INDEX idx_scans_user_created ON scans(user_id, created_at DESC);
