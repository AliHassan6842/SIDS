package com.agrosense.scan.infrastructure;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.OffsetDateTime;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

class ScanRepositoryOwnershipTest {
    private JdbcTemplate jdbc;
    private ScanRepository repository;

    @BeforeEach
    void setUp() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource(
            "jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DB_CLOSE_DELAY=-1", "sa", "");
        jdbc = new JdbcTemplate(dataSource);
        jdbc.execute("CREATE TABLE crops(id UUID PRIMARY KEY, slug VARCHAR(64), name VARCHAR(120), image_url VARCHAR(255), identification_supported BOOLEAN)");
        jdbc.execute("CREATE TABLE pests(id UUID PRIMARY KEY, slug VARCHAR(96))");
        jdbc.execute("CREATE TABLE scans(id UUID PRIMARY KEY, user_id UUID NOT NULL, identification_mode VARCHAR(32), crop_id UUID, image_key VARCHAR(255), status VARCHAR(32), training_consent BOOLEAN, consented_at TIMESTAMP WITH TIME ZONE, created_at TIMESTAMP WITH TIME ZONE)");
        jdbc.execute("CREATE TABLE scan_predictions(scan_id UUID PRIMARY KEY, pest_id UUID, confidence DECIMAL(7,6), bbox_x DECIMAL(8,7), bbox_y DECIMAL(8,7), bbox_width DECIMAL(8,7), bbox_height DECIMAL(8,7), model_id VARCHAR(120), model_version VARCHAR(80), dataset_version VARCHAR(120), result_type VARCHAR(32), reason VARCHAR(64))");
        jdbc.execute("CREATE TABLE scan_reviews(id UUID PRIMARY KEY, scan_id UUID, status VARCHAR(16), created_at TIMESTAMP WITH TIME ZONE)");
        repository = new ScanRepository(jdbc);
    }

    @Test
    void userCannotFetchAnotherUsersScan() {
        UUID ownerId = UUID.randomUUID();
        UUID otherUserId = UUID.randomUUID();
        UUID cropId = UUID.randomUUID();
        UUID scanId = UUID.randomUUID();
        jdbc.update("INSERT INTO crops(id,slug,name,identification_supported) VALUES (?,?,?,?)", cropId, "cotton", "Cotton", false);
        jdbc.update("INSERT INTO scans(id,user_id,identification_mode,crop_id,image_key,status,training_consent,created_at) VALUES (?,?,?,?,?,?,?,?)",
            scanId, ownerId, "CROP_PEST", cropId, ownerId + "/" + scanId + ".jpg", "UNKNOWN", false, OffsetDateTime.now());
        jdbc.update("INSERT INTO scan_predictions(scan_id,result_type,reason) VALUES (?,?,?)", scanId, "UNKNOWN", "LOW_CONFIDENCE");

        assertThat(repository.get(scanId, ownerId)).isPresent();
        assertThat(repository.get(scanId, otherUserId)).isEmpty();
    }
}
