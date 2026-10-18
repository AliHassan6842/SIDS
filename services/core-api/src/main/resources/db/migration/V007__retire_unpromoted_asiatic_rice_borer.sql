DELETE FROM pest_guidance
WHERE pest_id = (
    SELECT id FROM pests WHERE slug = 'asiatic-rice-borer'
);

DELETE FROM crop_pests
WHERE pest_id = (
    SELECT id FROM pests WHERE slug = 'asiatic-rice-borer'
);

UPDATE pests
SET supported = FALSE
WHERE slug = 'asiatic-rice-borer';
