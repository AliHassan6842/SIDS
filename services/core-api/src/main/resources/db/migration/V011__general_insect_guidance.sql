CREATE TABLE general_insect_guidance (
    pest_id UUID PRIMARY KEY REFERENCES pests(id) ON DELETE CASCADE,
    harm_summary TEXT NOT NULL,
    safe_removal TEXT NOT NULL,
    seek_expert_help_when TEXT NOT NULL,
    source_name VARCHAR(255) NOT NULL,
    source_url TEXT NOT NULL,
    last_verified_at DATE NOT NULL
);
