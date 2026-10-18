package com.agrosense.migration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.sql.DriverManager;
import java.util.Set;
import java.util.TreeSet;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.postgresql.PostgreSQLContainer;

@Testcontainers(disabledWithoutDocker = true)
class FlywayMigrationCompatibilityTest {
    @Container
    static final PostgreSQLContainer postgres = new PostgreSQLContainer("postgres:16-alpine");

    @Test
    void appliesSimplifiedMigrationAfterAllLegacyMigrations() throws Exception {
        var result = Flyway.configure()
            .dataSource(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword())
            .locations("classpath:db/migration")
            .load()
            .migrate();

        assertThat(result.migrationsExecuted).isEqualTo(11);
        assertThat(tableNames()).contains(
            "users", "observations", "diagnoses", "tasks",
            "crops", "pests", "crop_pests", "pest_guidance", "scans", "scan_predictions",
            "scan_reviews", "scan_review_events", "scan_training_consent_events",
            "model_promotions", "model_promotion_reviews", "general_insect_guidance");
        assertThat(columnNames("users")).contains("sub", "password_hash", "language", "system_role");
        assertThat(columnNames("scans")).contains(
            "id", "user_id", "crop_id", "image_key", "status", "created_at",
            "identification_mode", "training_consent", "consented_at");
        assertThat(columnNames("crops")).contains("image_url", "identification_supported");
        assertThat(columnNames("pests")).contains("image_url", "pest_kind");
        assertThat(isNullable("pests", "scientific_name")).isTrue();
        assertThat(isNullable("users", "sub")).isTrue();
        assertThat(supportedSlugs()).containsExactly(
            "rice-leaf-roller", "rice-water-weevil");
        assertThat(countRows("general_insect_guidance")).isZero();

        var dataSource = new DriverManagerDataSource(
            postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword());
        var catalog = new com.agrosense.catalog.infrastructure.CatalogRepository(new JdbcTemplate(dataSource));
        assertThat(catalog.pests(null)).extracting("slug").containsExactly(
            "rice-leaf-roller", "rice-water-weevil");
        assertThat(catalog.crops()).extracting("imageUrl").containsExactly("/catalog/crops/rice.jpg");
        assertThat(catalog.crops(true)).extracting("slug").containsExactly(
            "beet", "citrus", "corn", "rice", "wheat");
        assertThat(catalog.crops(true)).filteredOn("identificationSupported", true)
            .extracting("slug").containsExactly("rice");
        assertThat(catalog.pests(null)).extracting("imageUrl").containsExactly(
            "/catalog/pests/rice-leaf-roller.jpg", "/catalog/pests/rice-water-weevil.jpg");

        UUIDsAndAuditChecks.assertWith(new JdbcTemplate(dataSource));
    }

    private static final class UUIDsAndAuditChecks {
        private static void assertWith(JdbcTemplate jdbc) {
            var userId = java.util.UUID.randomUUID();
            var promotionId = java.util.UUID.randomUUID();
            var now = java.time.OffsetDateTime.now();
            jdbc.update("INSERT INTO users(id,sub,email,name,created_at,updated_at,system_role) VALUES (?,?,?,?,?,?,?)",
                userId, "local:" + userId, "admin@example.test", "Admin", now, now, "ADMIN");
            jdbc.update("INSERT INTO model_promotions(id,model_id,model_version,dataset_version,manifest_sha256,artifact_sha256,promoted_by,promoted_at) VALUES (?,?,?,?,?,?,?,?)",
                promotionId, "sids-detector", "2.0.0", "dataset-v2", "a".repeat(64), "b".repeat(64), userId, now);

            assertThatThrownBy(() -> jdbc.update("UPDATE model_promotions SET model_version='tampered' WHERE id=?", promotionId))
                .isInstanceOf(org.springframework.dao.DataAccessException.class);

            var generalScan = java.util.UUID.randomUUID();
            jdbc.update("INSERT INTO scans(id,user_id,identification_mode,crop_id,image_key,status,training_consent,created_at) VALUES (?,?,?,?,?,?,?,?)",
                generalScan, userId, "GENERAL_INSECT", null, "private/general.jpg", "UNKNOWN", false, now);
            assertThat(jdbc.queryForObject("SELECT crop_id IS NULL FROM scans WHERE id=?", Boolean.class, generalScan)).isTrue();
            assertThatThrownBy(() -> jdbc.update("INSERT INTO scans(id,user_id,identification_mode,crop_id,image_key,status,training_consent,created_at) VALUES (?,?,?,?,?,?,?,?)",
                java.util.UUID.randomUUID(), userId, "GENERAL_INSECT", java.util.UUID.fromString("10000000-0000-0000-0000-000000000001"),
                "private/invalid.jpg", "UNKNOWN", false, now)).isInstanceOf(org.springframework.dao.DataAccessException.class);
        }
    }

    private Set<String> tableNames() throws Exception {
        try (var connection = DriverManager.getConnection(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword());
             var statement = connection.prepareStatement(
                 "SELECT table_name FROM information_schema.tables WHERE table_schema='public'");
             var result = statement.executeQuery()) {
            Set<String> names = new TreeSet<>();
            while (result.next()) names.add(result.getString(1));
            return names;
        }
    }

    private Set<String> columnNames(String table) throws Exception {
        try (var connection = DriverManager.getConnection(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword());
             var statement = connection.prepareStatement(
                 "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=?")) {
            statement.setString(1, table);
            try (var result = statement.executeQuery()) {
                Set<String> names = new TreeSet<>();
                while (result.next()) names.add(result.getString(1));
                return names;
            }
        }
    }

    private boolean isNullable(String table, String column) throws Exception {
        try (var connection = DriverManager.getConnection(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword());
             var statement = connection.prepareStatement(
                 "SELECT is_nullable FROM information_schema.columns WHERE table_schema='public' AND table_name=? AND column_name=?")) {
            statement.setString(1, table);
            statement.setString(2, column);
            try (var result = statement.executeQuery()) {
                assertThat(result.next()).isTrue();
                return "YES".equals(result.getString(1));
            }
        }
    }

    private Set<String> supportedSlugs() throws Exception {
        try (var connection = DriverManager.getConnection(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword());
             var statement = connection.prepareStatement("SELECT slug FROM pests WHERE supported=TRUE ORDER BY slug");
             var result = statement.executeQuery()) {
            Set<String> slugs = new TreeSet<>();
            while (result.next()) slugs.add(result.getString(1));
            return slugs;
        }
    }

    private int countRows(String table) throws Exception {
        try (var connection = DriverManager.getConnection(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword());
             var statement = connection.prepareStatement("SELECT COUNT(*) FROM " + table);
             var result = statement.executeQuery()) {
            assertThat(result.next()).isTrue();
            return result.getInt(1);
        }
    }
}
