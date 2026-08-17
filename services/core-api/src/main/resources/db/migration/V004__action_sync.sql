CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL, -- RESCOUT, FOLLOW_UP, INSPECTION, TREATMENT_FOLLOW_UP, EXPERT_REVIEW
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    due_at TIMESTAMP WITH TIME ZONE,
    user_id UUID,
    farm_id UUID NOT NULL,
    field_id UUID,
    recommendation_id UUID,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE weather_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    precipitation DECIMAL(5, 2),
    wind DECIMAL(5, 2),
    provider VARCHAR(50) NOT NULL,
    raw_metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL, -- TASK_DUE, RESCOUT_DUE, ANALYSIS_COMPLETE, EXPERT_REVIEW_REQUIRED
    user_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL, -- UNREAD, READ
    message TEXT NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE sync_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_event_id VARCHAR(255) NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    base_version BIGINT,
    created_at_device TIMESTAMP WITH TIME ZONE NOT NULL,
    server_received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE idempotency_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_event_id VARCHAR(255) UNIQUE NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL,
    user_id UUID,
    entity_type VARCHAR(50),
    entity_id UUID,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_farm_status ON tasks(user_id, farm_id, status, due_at);
CREATE INDEX idx_weather_snapshots_field_timestamp ON weather_snapshots(field_id, timestamp);
CREATE INDEX idx_notifications_user_status ON notifications(user_id, status);
CREATE INDEX idx_idempotency_records_client_event_id ON idempotency_records(client_event_id);
