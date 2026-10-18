CREATE EXTENSION IF NOT EXISTS "pgcrypto";

DO $$ 
DECLARE
    beetle_id UUID := gen_random_uuid();
    grasshopper_id UUID := gen_random_uuid();
    mosquito_id UUID := gen_random_uuid();
BEGIN
    INSERT INTO pests (id, slug, pest_kind, common_name, scientific_name, description, supported) VALUES
    (beetle_id, 'beetle', 'GENERAL_INSECT', 'Beetle', 'Coleoptera', 'General beetle group.', TRUE),
    (grasshopper_id, 'grasshopper', 'GENERAL_INSECT', 'Grasshopper', 'Caelifera', 'General grasshopper group.', TRUE),
    (mosquito_id, 'mosquito', 'GENERAL_INSECT', 'Mosquito', 'Culicidae', 'General mosquito group.', TRUE);

    INSERT INTO general_insect_guidance (pest_id, harm_summary, safe_removal, seek_expert_help_when, source_name, source_url, last_verified_at) VALUES
    (beetle_id, 'Most beetles are harmless or beneficial, but some can damage crops or household goods.', 'Carefully sweep or capture in a cup to release outside.', 'If structural damage is observed or a large indoor infestation occurs.', 'University Extension', 'https://example.edu/beetles', CURRENT_DATE),
    (grasshopper_id, 'Generally harmless to humans but can cause significant defoliation to crops and gardens.', 'Hand-pick or use physical barriers like row covers.', 'When crop defoliation exceeds acceptable thresholds.', 'University Extension', 'https://example.edu/grasshoppers', CURRENT_DATE),
    (mosquito_id, 'Can cause itchy bites and potentially transmit diseases depending on the region.', 'Eliminate standing water, use screens, and apply approved repellents.', 'If local health advisories indicate disease risk.', 'Public Health Department', 'https://example.gov/mosquitoes', CURRENT_DATE);
END $$;
