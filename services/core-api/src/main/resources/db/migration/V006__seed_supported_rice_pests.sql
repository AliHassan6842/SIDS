UPDATE crops SET supported = FALSE WHERE slug <> 'rice';
UPDATE pests SET supported = FALSE
WHERE slug NOT IN ('rice-leaf-roller', 'asiatic-rice-borer', 'rice-water-weevil');

INSERT INTO crops (id, slug, name, supported)
VALUES ('10000000-0000-0000-0000-000000000001', 'rice', 'Rice', TRUE)
ON CONFLICT (slug) DO UPDATE
SET name = EXCLUDED.name, supported = EXCLUDED.supported;

INSERT INTO pests (id, slug, common_name, scientific_name, description, supported)
VALUES
    ('20000000-0000-0000-0000-000000000001', 'rice-leaf-roller', 'Rice leaf roller',
     'Cnaphalocrocis medinalis',
     'A rice-feeding moth whose larvae fold leaves and feed within the folded leaf tissue.', TRUE),
    ('20000000-0000-0000-0000-000000000004', 'asiatic-rice-borer', 'Asiatic rice borer',
     'Chilo suppressalis',
     'A stem-boring moth whose larvae feed inside rice stems and can interrupt plant growth.', TRUE),
    ('20000000-0000-0000-0000-000000000011', 'rice-water-weevil', 'Rice water weevil',
     'Lissorhoptrus oryzophilus',
     'A rice pest whose adults feed on leaves and whose larvae feed on roots in flooded fields.', TRUE)
ON CONFLICT (slug) DO UPDATE
SET common_name = EXCLUDED.common_name,
    scientific_name = EXCLUDED.scientific_name,
    description = EXCLUDED.description,
    supported = EXCLUDED.supported;

INSERT INTO crop_pests (crop_id, pest_id)
SELECT c.id, p.id
FROM crops c
CROSS JOIN pests p
WHERE c.slug = 'rice'
  AND p.slug IN ('rice-leaf-roller', 'asiatic-rice-borer', 'rice-water-weevil')
ON CONFLICT DO NOTHING;

INSERT INTO pest_guidance (
    pest_id, damage_description, prevention, basic_management, expert_advice_note,
    source_name, source_url, last_verified_at
)
SELECT p.id,
       'Larvae fold rice leaves and scrape green tissue, leaving pale feeding areas and reducing useful leaf surface.',
       E'Use balanced nitrogen and avoid excessive nitrogen.\nConserve spiders and other natural enemies.\nAvoid unnecessary early intervention when visible injury is limited; rice can compensate for early injury.',
       E'Inspect folded leaves to confirm larvae are present.\nRemove heavily affected leaves in small plantings where practical.\nSeek local expert advice if damage is widespread.',
       'Identification alone does not determine whether pesticide treatment is required.',
       'IRRI Rice Knowledge Bank — Insects',
       'https://www.knowledgebank.irri.org/step-by-step-production/growth/pests-and-diseases/insects',
       DATE '2026-08-22'
FROM pests p WHERE p.slug = 'rice-leaf-roller'
ON CONFLICT (pest_id) DO UPDATE
SET damage_description = EXCLUDED.damage_description,
    prevention = EXCLUDED.prevention,
    basic_management = EXCLUDED.basic_management,
    expert_advice_note = EXCLUDED.expert_advice_note,
    source_name = EXCLUDED.source_name,
    source_url = EXCLUDED.source_url,
    last_verified_at = EXCLUDED.last_verified_at;

INSERT INTO pest_guidance (
    pest_id, damage_description, prevention, basic_management, expert_advice_note,
    source_name, source_url, last_verified_at
)
SELECT p.id,
       'Larvae tunnel inside rice stems, which can cause dead central shoots or empty, pale panicles.',
       E'Remove or destroy rice stubble after harvest where locally appropriate.\nUse balanced crop nutrition.\nConserve natural enemies and inspect plants regularly.',
       E'Check affected stems for boring damage or larvae.\nRemove badly affected plants in small plantings where practical.\nSeek local expert advice when stem damage is spreading.',
       'Identification alone does not determine whether pesticide treatment is required.',
       'IRRI Rice Knowledge Bank — Stem borer',
       'https://www.knowledgebank.irri.org/training/fact-sheets/pest-management/insects/item/stem-borer',
       DATE '2026-08-22'
FROM pests p WHERE p.slug = 'asiatic-rice-borer'
ON CONFLICT (pest_id) DO UPDATE
SET damage_description = EXCLUDED.damage_description,
    prevention = EXCLUDED.prevention,
    basic_management = EXCLUDED.basic_management,
    expert_advice_note = EXCLUDED.expert_advice_note,
    source_name = EXCLUDED.source_name,
    source_url = EXCLUDED.source_url,
    last_verified_at = EXCLUDED.last_verified_at;

INSERT INTO pest_guidance (
    pest_id, damage_description, prevention, basic_management, expert_advice_note,
    source_name, source_url, last_verified_at
)
SELECT p.id,
       'Adults scar rice leaves while larvae feed on roots, which can reduce root function and plant vigor.',
       E'Inspect young rice for adult leaf scars.\nInspect roots for larvae when poor growth is observed.\nAsk a local rice specialist whether planting or water-management changes are appropriate for the local production system.',
       E'Confirm adult leaf scars and inspect roots for larvae where feasible.\nRecord affected areas and monitor plant recovery.\nConsult a local rice specialist if root injury or stand loss is substantial.',
       'Identification alone does not determine whether pesticide treatment is required.',
       'LSU AgCenter — Rice Water Weevil',
       'https://www.lsuagcenter.com/topics/crops/rice/insects/presentations/1-rice-water-weevil',
       DATE '2026-08-22'
FROM pests p WHERE p.slug = 'rice-water-weevil'
ON CONFLICT (pest_id) DO UPDATE
SET damage_description = EXCLUDED.damage_description,
    prevention = EXCLUDED.prevention,
    basic_management = EXCLUDED.basic_management,
    expert_advice_note = EXCLUDED.expert_advice_note,
    source_name = EXCLUDED.source_name,
    source_url = EXCLUDED.source_url,
    last_verified_at = EXCLUDED.last_verified_at;
