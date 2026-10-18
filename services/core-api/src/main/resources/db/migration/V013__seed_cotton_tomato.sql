CREATE EXTENSION IF NOT EXISTS "pgcrypto";

INSERT INTO crops (id, slug, name, supported, image_url) VALUES
    (gen_random_uuid(), 'cotton', 'Cotton', TRUE, '/catalog/crops/cotton.jpg'),
    (gen_random_uuid(), 'tomato', 'Tomato', TRUE, '/catalog/crops/tomato.jpg')
ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, supported = EXCLUDED.supported, image_url = EXCLUDED.image_url;

INSERT INTO pests (id, slug, pest_kind, common_name, scientific_name, description, supported, image_url) VALUES
    (gen_random_uuid(), 'cotton-whitefly', 'CROP_PEST', 'Whitefly', 'Bemisia tabaci', 'Whitefly affects cotton.', TRUE, '/catalog/pests/cotton-whitefly.jpg'),
    (gen_random_uuid(), 'cotton-jassid', 'CROP_PEST', 'Jassid', 'Amrasca biguttula', 'Jassid affects cotton.', TRUE, '/catalog/pests/cotton-jassid.jpg'),
    (gen_random_uuid(), 'cotton-thrips', 'CROP_PEST', 'Thrips', 'Thrips tabaci', 'Thrips affects cotton.', TRUE, '/catalog/pests/cotton-thrips.jpg'),
    (gen_random_uuid(), 'cotton-mealybug', 'CROP_PEST', 'Mealybug', 'Phenacoccus solenopsis', 'Mealybug affects cotton.', TRUE, '/catalog/pests/cotton-mealybug.jpg'),
    (gen_random_uuid(), 'pink-bollworm', 'CROP_PEST', 'Pink Bollworm', 'Pectinophora gossypiella', 'Pink Bollworm affects cotton.', TRUE, '/catalog/pests/pink-bollworm.jpg'),
    (gen_random_uuid(), 'spotted-bollworm', 'CROP_PEST', 'Spotted Bollworm', 'Earias vittella', 'Spotted Bollworm affects cotton.', TRUE, '/catalog/pests/spotted-bollworm.jpg'),
    (gen_random_uuid(), 'american-bollworm', 'CROP_PEST', 'American Bollworm', 'Helicoverpa armigera', 'American Bollworm affects cotton.', TRUE, '/catalog/pests/american-bollworm.jpg'),
    (gen_random_uuid(), 'cotton-leaf-curl', 'CROP_PEST', 'Cotton Leaf Curl Virus', 'Begomovirus', 'Cotton Leaf Curl Virus affects cotton.', TRUE, '/catalog/pests/cotton-leaf-curl.jpg'),
    (gen_random_uuid(), 'tomato-early-blight', 'CROP_PEST', 'Early Blight', 'Alternaria solani', 'Early Blight affects tomato.', TRUE, '/catalog/pests/tomato-early-blight.jpg'),
    (gen_random_uuid(), 'tomato-late-blight', 'CROP_PEST', 'Late Blight', 'Phytophthora infestans', 'Late Blight affects tomato.', TRUE, '/catalog/pests/tomato-late-blight.jpg'),
    (gen_random_uuid(), 'tomato-bacterial-spot', 'CROP_PEST', 'Bacterial Spot', 'Xanthomonas campestris pv. vesicatoria', 'Bacterial Spot affects tomato.', TRUE, '/catalog/pests/tomato-bacterial-spot.jpg'),
    (gen_random_uuid(), 'tomato-yellow-leaf-curl-virus', 'CROP_PEST', 'Yellow Leaf Curl Virus', 'Tomato yellow leaf curl virus', 'Yellow Leaf Curl Virus affects tomato.', TRUE, '/catalog/pests/tomato-yellow-leaf-curl-virus.jpg')
ON CONFLICT (slug) DO UPDATE SET pest_kind = EXCLUDED.pest_kind, common_name = EXCLUDED.common_name, scientific_name = EXCLUDED.scientific_name, description = EXCLUDED.description, supported = EXCLUDED.supported, image_url = EXCLUDED.image_url;

INSERT INTO crop_pests (crop_id, pest_id)
SELECT c.id, p.id FROM crops c CROSS JOIN pests p
WHERE (c.slug = 'cotton' AND p.slug IN ('cotton-whitefly', 'cotton-jassid', 'cotton-thrips', 'cotton-mealybug', 'pink-bollworm', 'spotted-bollworm', 'american-bollworm', 'cotton-leaf-curl'))
   OR (c.slug = 'tomato' AND p.slug IN ('tomato-early-blight', 'tomato-late-blight', 'tomato-bacterial-spot', 'tomato-yellow-leaf-curl-virus'))
ON CONFLICT DO NOTHING;

INSERT INTO pest_guidance (pest_id, damage_description, prevention, basic_management, expert_advice_note, source_name, source_url, last_verified_at) VALUES
    ( (SELECT id FROM pests WHERE slug = 'cotton-whitefly'), 'Damage to COTTON', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/cotton-whitefly', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'cotton-jassid'), 'Damage to COTTON', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/cotton-jassid', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'cotton-thrips'), 'Damage to COTTON', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/cotton-thrips', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'cotton-mealybug'), 'Damage to COTTON', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/cotton-mealybug', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'pink-bollworm'), 'Damage to COTTON', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/pink-bollworm', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'spotted-bollworm'), 'Damage to COTTON', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/spotted-bollworm', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'american-bollworm'), 'Damage to COTTON', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/american-bollworm', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'cotton-leaf-curl'), 'Damage to COTTON', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/cotton-leaf-curl', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'tomato-early-blight'), 'Damage to TOMATO', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/tomato-early-blight', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'tomato-late-blight'), 'Damage to TOMATO', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/tomato-late-blight', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'tomato-bacterial-spot'), 'Damage to TOMATO', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/tomato-bacterial-spot', CURRENT_DATE ),
    ( (SELECT id FROM pests WHERE slug = 'tomato-yellow-leaf-curl-virus'), 'Damage to TOMATO', 'Prevent by monitoring.', 'Manage using appropriate methods.', 'Seek expert advice if needed.', 'Local Agriculture Dept', 'https://example.com/tomato-yellow-leaf-curl-virus', CURRENT_DATE )
ON CONFLICT (pest_id) DO UPDATE SET damage_description = EXCLUDED.damage_description, prevention = EXCLUDED.prevention, basic_management = EXCLUDED.basic_management, expert_advice_note = EXCLUDED.expert_advice_note, source_name = EXCLUDED.source_name, source_url = EXCLUDED.source_url, last_verified_at = EXCLUDED.last_verified_at;
