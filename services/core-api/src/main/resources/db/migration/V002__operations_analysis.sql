CREATE TABLE observations (
    id UUID PRIMARY KEY,
    farm_id UUID NOT NULL REFERENCES farms(id),
    field_id UUID NOT NULL REFERENCES fields(id),
    crop_cycle_id UUID NOT NULL REFERENCES crop_cycles(id),
    user_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE samples (
    id UUID PRIMARY KEY,
    observation_id UUID NOT NULL REFERENCES observations(id),
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE images (
    id UUID PRIMARY KEY,
    observation_id UUID NOT NULL REFERENCES observations(id),
    sample_id UUID REFERENCES samples(id),
    object_key VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    size_bytes BIGINT,
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE survey_protocols (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    crop_id VARCHAR(100) NOT NULL,
    problem_id VARCHAR(100),
    growth_stage VARCHAR(100),
    minimum_samples INTEGER NOT NULL,
    sampling_unit VARCHAR(50) NOT NULL,
    measure_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE field_surveys (
    id UUID PRIMARY KEY,
    farm_id UUID NOT NULL REFERENCES farms(id),
    field_id UUID NOT NULL REFERENCES fields(id),
    protocol_id UUID NOT NULL REFERENCES survey_protocols(id),
    observation_id UUID REFERENCES observations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE survey_points (
    id UUID PRIMARY KEY,
    survey_id UUID NOT NULL REFERENCES field_surveys(id),
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE survey_measurements (
    id UUID PRIMARY KEY,
    point_id UUID NOT NULL REFERENCES survey_points(id),
    measure_type VARCHAR(50) NOT NULL,
    value DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE analysis_jobs (
    id UUID PRIMARY KEY,
    observation_id UUID NOT NULL REFERENCES observations(id),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE diagnoses (
    id UUID PRIMARY KEY,
    analysis_job_id UUID NOT NULL REFERENCES analysis_jobs(id),
    observation_id UUID NOT NULL REFERENCES observations(id),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE detections (
    id UUID PRIMARY KEY,
    diagnosis_id UUID NOT NULL REFERENCES diagnoses(id),
    image_id UUID NOT NULL REFERENCES images(id),
    bbox_x DECIMAL(10, 2),
    bbox_y DECIMAL(10, 2),
    bbox_w DECIMAL(10, 2),
    bbox_h DECIMAL(10, 2),
    confidence DECIMAL(5, 4),
    label VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE classifications (
    id UUID PRIMARY KEY,
    diagnosis_id UUID NOT NULL REFERENCES diagnoses(id),
    image_id UUID NOT NULL REFERENCES images(id),
    label VARCHAR(100) NOT NULL,
    confidence DECIMAL(5, 4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE severity_assessments (
    id UUID PRIMARY KEY,
    diagnosis_id UUID NOT NULL REFERENCES diagnoses(id),
    image_id UUID REFERENCES images(id),
    sample_id UUID REFERENCES samples(id),
    severity_level VARCHAR(50) NOT NULL,
    score DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
