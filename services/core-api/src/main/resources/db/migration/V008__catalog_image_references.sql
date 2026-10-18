ALTER TABLE crops ADD COLUMN image_url VARCHAR(255);
ALTER TABLE pests ADD COLUMN image_url VARCHAR(255);

UPDATE crops
SET image_url = '/catalog/crops/rice.jpg'
WHERE slug = 'rice';

UPDATE pests
SET image_url = CASE slug
    WHEN 'rice-leaf-roller' THEN '/catalog/pests/rice-leaf-roller.jpg'
    WHEN 'rice-water-weevil' THEN '/catalog/pests/rice-water-weevil.jpg'
    ELSE image_url
END
WHERE slug IN ('rice-leaf-roller', 'rice-water-weevil');
