ALTER TABLE users
    ADD COLUMN system_role VARCHAR(16) NOT NULL DEFAULT 'USER';

ALTER TABLE users
    ADD CONSTRAINT ck_users_system_role
    CHECK (system_role IN ('USER', 'REVIEWER', 'ADMIN'));

ALTER TABLE crops
    ADD COLUMN identification_supported BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE pests
    ADD COLUMN pest_kind VARCHAR(32) NOT NULL DEFAULT 'CROP_PEST';

ALTER TABLE pests
    ADD CONSTRAINT ck_pests_kind
    CHECK (pest_kind IN ('CROP_PEST', 'GENERAL_INSECT'));

UPDATE crops
SET identification_supported = supported;

INSERT INTO crops (id, slug, name, supported, identification_supported, image_url)
VALUES
    ('10000000-0000-0000-0000-000000000001', 'rice', 'Rice', TRUE, TRUE, '/catalog/crops/rice.jpg'),
    ('10000000-0000-0000-0000-000000000002', 'corn', 'Corn', TRUE, FALSE, NULL),
    ('10000000-0000-0000-0000-000000000003', 'wheat', 'Wheat', TRUE, FALSE, NULL),
    ('10000000-0000-0000-0000-000000000004', 'beet', 'Beet', TRUE, FALSE, NULL),
    ('10000000-0000-0000-0000-000000000005', 'citrus', 'Citrus', TRUE, FALSE, NULL)
ON CONFLICT (slug) DO UPDATE
SET name = EXCLUDED.name,
    supported = EXCLUDED.supported,
    identification_supported = EXCLUDED.identification_supported,
    image_url = COALESCE(crops.image_url, EXCLUDED.image_url);

ALTER TABLE scans
    ADD COLUMN identification_mode VARCHAR(32) NOT NULL DEFAULT 'CROP_PEST',
    ADD COLUMN training_consent BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN consented_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE scans
    ALTER COLUMN crop_id DROP NOT NULL;

ALTER TABLE scans
    ADD CONSTRAINT ck_scans_identification_mode
    CHECK (identification_mode IN ('CROP_PEST', 'GENERAL_INSECT')),
    ADD CONSTRAINT ck_scans_mode_crop
    CHECK (
        (identification_mode = 'CROP_PEST' AND crop_id IS NOT NULL)
        OR (identification_mode = 'GENERAL_INSECT' AND crop_id IS NULL)
    ),
    ADD CONSTRAINT ck_scans_consent_timestamp
    CHECK (
        (training_consent = TRUE AND consented_at IS NOT NULL)
        OR (training_consent = FALSE AND consented_at IS NULL)
    );

CREATE TABLE scan_training_consent_events (
    id UUID PRIMARY KEY,
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    actor_user_id UUID NOT NULL REFERENCES users(id),
    consented BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_scan_training_consent_events_scan
    ON scan_training_consent_events(scan_id, created_at DESC);

CREATE TABLE scan_reviews (
    id UUID PRIMARY KEY,
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    submitted_by UUID NOT NULL REFERENCES users(id),
    proposed_label_slug VARCHAR(96),
    submission_notes VARCHAR(1000),
    status VARCHAR(16) NOT NULL CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    assigned_reviewer_id UUID REFERENCES users(id),
    claimed_at TIMESTAMP WITH TIME ZONE,
    reviewer_label_slug VARCHAR(96),
    reviewer_notes VARCHAR(1000),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT ck_scan_reviews_claim_pair CHECK (
        (assigned_reviewer_id IS NULL AND claimed_at IS NULL)
        OR (assigned_reviewer_id IS NOT NULL AND claimed_at IS NOT NULL)
    ),
    CONSTRAINT ck_scan_reviews_decision_time CHECK (
        (status = 'PENDING' AND reviewed_at IS NULL)
        OR (status IN ('APPROVED', 'REJECTED') AND reviewed_at IS NOT NULL)
    )
);

CREATE UNIQUE INDEX uq_scan_reviews_one_pending
    ON scan_reviews(scan_id)
    WHERE status = 'PENDING';

CREATE INDEX idx_scan_reviews_queue
    ON scan_reviews(status, assigned_reviewer_id, created_at);

CREATE TABLE scan_review_events (
    id UUID PRIMARY KEY,
    review_id UUID NOT NULL REFERENCES scan_reviews(id) ON DELETE CASCADE,
    actor_user_id UUID NOT NULL REFERENCES users(id),
    event_type VARCHAR(32) NOT NULL CHECK (
        event_type IN ('SUBMITTED', 'CLAIMED', 'APPROVED', 'REJECTED', 'CONSENT_WITHDRAWN')
    ),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_scan_review_events_review
    ON scan_review_events(review_id, created_at);

CREATE TABLE model_promotions (
    id UUID PRIMARY KEY,
    model_id VARCHAR(120) NOT NULL,
    model_version VARCHAR(80) NOT NULL,
    dataset_version VARCHAR(120) NOT NULL,
    manifest_sha256 CHAR(64) NOT NULL CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    artifact_sha256 CHAR(64) NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_promotion_id UUID REFERENCES model_promotions(id),
    promoted_by UUID NOT NULL REFERENCES users(id),
    promoted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (model_id, model_version, dataset_version)
);

CREATE TABLE model_promotion_reviews (
    promotion_id UUID NOT NULL REFERENCES model_promotions(id) ON DELETE RESTRICT,
    review_id UUID NOT NULL REFERENCES scan_reviews(id) ON DELETE RESTRICT,
    PRIMARY KEY (promotion_id, review_id)
);

CREATE OR REPLACE FUNCTION sids_prevent_audit_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION '% is append-only', TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_consent_event_mutation
    BEFORE UPDATE OR DELETE ON scan_training_consent_events
    FOR EACH ROW EXECUTE FUNCTION sids_prevent_audit_mutation();

CREATE TRIGGER prevent_review_event_mutation
    BEFORE UPDATE OR DELETE ON scan_review_events
    FOR EACH ROW EXECUTE FUNCTION sids_prevent_audit_mutation();

CREATE TRIGGER prevent_model_promotion_mutation
    BEFORE UPDATE OR DELETE ON model_promotions
    FOR EACH ROW EXECUTE FUNCTION sids_prevent_audit_mutation();

CREATE TRIGGER prevent_model_promotion_review_mutation
    BEFORE UPDATE OR DELETE ON model_promotion_reviews
    FOR EACH ROW EXECUTE FUNCTION sids_prevent_audit_mutation();
