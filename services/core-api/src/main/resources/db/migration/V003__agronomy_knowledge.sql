CREATE TABLE recommendations (
    id UUID PRIMARY KEY,
    diagnosis_id UUID REFERENCES diagnoses(id),
    action_category VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE recommendation_evidence (
    id UUID PRIMARY KEY,
    recommendation_id UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    evidence_type VARCHAR(50) NOT NULL,
    reference_id VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL
);

CREATE TABLE treatments (
    id UUID PRIMARY KEY,
    recommendation_id UUID REFERENCES recommendations(id),
    field_id UUID NOT NULL REFERENCES fields(id),
    treatment_type VARCHAR(50) NOT NULL,
    product_name VARCHAR(255),
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    outcome VARCHAR(50),
    follow_up_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
