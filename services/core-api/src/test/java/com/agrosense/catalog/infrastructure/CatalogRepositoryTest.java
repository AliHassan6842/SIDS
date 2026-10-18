package com.agrosense.catalog.infrastructure;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDate;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

class CatalogRepositoryTest {
    private JdbcTemplate jdbc;
    private CatalogRepository repository;
    private UUID riceId;
    private UUID leafRollerId;
    private UUID generalInsectId;

    @BeforeEach
    void setUp() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource(
            "jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DB_CLOSE_DELAY=-1", "sa", "");
        jdbc = new JdbcTemplate(dataSource);
        jdbc.execute("CREATE TABLE crops(id UUID PRIMARY KEY, slug VARCHAR(64), name VARCHAR(120), supported BOOLEAN, image_url VARCHAR(255), identification_supported BOOLEAN)");
        jdbc.execute("CREATE TABLE pests(id UUID PRIMARY KEY, slug VARCHAR(96), common_name VARCHAR(160), scientific_name VARCHAR(200), description VARCHAR(1000), supported BOOLEAN, image_url VARCHAR(255), pest_kind VARCHAR(32))");
        jdbc.execute("CREATE TABLE crop_pests(crop_id UUID, pest_id UUID, PRIMARY KEY(crop_id,pest_id))");
        jdbc.execute("CREATE TABLE pest_guidance(pest_id UUID PRIMARY KEY, damage_description VARCHAR(1000), prevention VARCHAR(1000), basic_management VARCHAR(1000), expert_advice_note VARCHAR(1000), source_name VARCHAR(255), source_url VARCHAR(1000), last_verified_at DATE)");
        jdbc.execute("CREATE TABLE general_insect_guidance(pest_id UUID PRIMARY KEY, harm_summary VARCHAR(1000), safe_removal VARCHAR(1000), seek_expert_help_when VARCHAR(1000), source_name VARCHAR(255), source_url VARCHAR(1000), last_verified_at DATE)");
        repository = new CatalogRepository(jdbc);
        riceId = UUID.randomUUID();
        leafRollerId = UUID.randomUUID();
        generalInsectId = UUID.randomUUID();
        UUID unrelatedPestId = UUID.randomUUID();
        jdbc.update("INSERT INTO crops VALUES (?,?,?,?,?,?)", riceId, "rice", "Rice", true, "/catalog/crops/rice.jpg", true);
        jdbc.update("INSERT INTO pests VALUES (?,?,?,?,?,?,?,?)", leafRollerId, "rice-leaf-roller", "Rice leaf roller", "Cnaphalocrocis medinalis", "Rice pest", true, "/catalog/pests/rice-leaf-roller.jpg", "CROP_PEST");
        jdbc.update("INSERT INTO pests VALUES (?,?,?,?,?,?,?,?)", unrelatedPestId, "other-pest", "Other pest", "Other species", "Other", true, null, "CROP_PEST");
        jdbc.update("INSERT INTO pests VALUES (?,?,?,?,?,?,?,?)", generalInsectId, "reviewed-general-insect", "Reviewed general insect", null,
            "A reviewed coarse insect category", true, null, "GENERAL_INSECT");
        jdbc.update("INSERT INTO crop_pests VALUES (?,?)", riceId, leafRollerId);
        jdbc.update("INSERT INTO pest_guidance VALUES (?,?,?,?,?,?,?,?)", leafRollerId, "Leaf damage", "Prevent one\nPrevent two", "Manage one", "Expert note", "IRRI", "https://example.test/irri", LocalDate.of(2026, 8, 22));
        jdbc.update("INSERT INTO general_insect_guidance VALUES (?,?,?,?,?,?,?)", generalInsectId,
            "Category-level harm summary", "Remove one\nRemove two", "Seek help one", "Reviewed source",
            "https://example.test/general", LocalDate.of(2026, 8, 26));
    }

    @Test
    void filtersPestsByCropUuid() {
        assertThat(repository.pests(riceId)).extracting("id").containsExactly(leafRollerId);
    }

    @Test
    void listsAllSupportedPestsWithoutANullSqlParameter() {
        assertThat(repository.pests(null)).extracting("slug")
            .containsExactly("other-pest", "reviewed-general-insect", "rice-leaf-roller");
    }

    @Test
    void loadsPestDetailsByUuid() {
        var pest = repository.pest(leafRollerId);

        assertThat(pest.slug()).isEqualTo("rice-leaf-roller");
        assertThat(pest.imageUrl()).isEqualTo("/catalog/pests/rice-leaf-roller.jpg");
        assertThat(pest.affectedCrops()).extracting("id").containsExactly(riceId);
        assertThat(pest.affectedCrops().getFirst().imageUrl()).isEqualTo("/catalog/crops/rice.jpg");
        assertThat(pest.guidance().sourceName()).isEqualTo("IRRI");
        assertThat(pest.guidance().prevention()).containsExactly("Prevent one", "Prevent two");
    }

    @Test
    void loadsGeneralGuidanceWithoutCropOrAgronomyGuidance() {
        var insect = repository.pest(generalInsectId);

        assertThat(insect.kind()).isEqualTo(com.agrosense.catalog.domain.PestKind.GENERAL_INSECT);
        assertThat(insect.scientificName()).isNull();
        assertThat(insect.affectedCrops()).isEmpty();
        assertThat(insect.guidance()).isNull();
        assertThat(insect.generalGuidance().harmSummary()).isEqualTo("Category-level harm summary");
        assertThat(insect.generalGuidance().safeRemoval()).containsExactly("Remove one", "Remove two");
        assertThat(insect.generalGuidance().sourceUrl()).isEqualTo("https://example.test/general");
        assertThat(repository.generalInsectId("reviewed-general-insect")).isEqualTo(generalInsectId);
        assertThat(repository.generalInsectId("rice-leaf-roller")).isNull();
    }
}
