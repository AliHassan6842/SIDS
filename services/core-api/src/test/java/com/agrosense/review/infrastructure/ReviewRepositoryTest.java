package com.agrosense.review.infrastructure;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.OffsetDateTime;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

class ReviewRepositoryTest {
    private JdbcTemplate jdbc;
    private ReviewRepository repository;
    private UUID ownerId;
    private UUID scanId;

    @BeforeEach
    void setUp() {
        var dataSource = new DriverManagerDataSource(
            "jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DB_CLOSE_DELAY=-1", "sa", "");
        jdbc = new JdbcTemplate(dataSource);
        jdbc.execute("CREATE TABLE scans(id UUID PRIMARY KEY,user_id UUID,identification_mode VARCHAR(32),status VARCHAR(32),training_consent BOOLEAN,consented_at TIMESTAMP WITH TIME ZONE,image_key VARCHAR(255))");
        jdbc.execute("CREATE TABLE scan_training_consent_events(id UUID PRIMARY KEY,scan_id UUID,actor_user_id UUID,consented BOOLEAN,created_at TIMESTAMP WITH TIME ZONE)");
        jdbc.execute("CREATE TABLE scan_reviews(id UUID PRIMARY KEY,scan_id UUID,submitted_by UUID,proposed_label_slug VARCHAR(96),submission_notes VARCHAR(1000),status VARCHAR(16),assigned_reviewer_id UUID,claimed_at TIMESTAMP WITH TIME ZONE,reviewer_label_slug VARCHAR(96),reviewer_notes VARCHAR(1000),reviewed_at TIMESTAMP WITH TIME ZONE,created_at TIMESTAMP WITH TIME ZONE)");
        jdbc.execute("CREATE TABLE scan_review_events(id UUID PRIMARY KEY,review_id UUID,actor_user_id UUID,event_type VARCHAR(32),created_at TIMESTAMP WITH TIME ZONE)");
        repository = new ReviewRepository(jdbc);
        ownerId = UUID.randomUUID();
        scanId = UUID.randomUUID();
        jdbc.update("INSERT INTO scans VALUES (?,?,?,?,?,?,?)", scanId, ownerId, "GENERAL_INSECT", "UNKNOWN", true, OffsetDateTime.now(), "owner/scan.jpg");
    }

    @Test
    void scanIntakeIsOwnerScoped() {
        assertThat(repository.ownedScan(scanId, ownerId)).isPresent();
        assertThat(repository.ownedScan(scanId, UUID.randomUUID())).isEmpty();
    }

    @Test
    void onlyOneReviewerCanOwnAClaim() {
        UUID reviewId = repository.submit(repository.ownedScan(scanId, ownerId).orElseThrow(), ownerId, null, null).id();
        UUID reviewerA = UUID.randomUUID();
        UUID reviewerB = UUID.randomUUID();

        assertThat(repository.claim(reviewId, reviewerA, OffsetDateTime.now())).isTrue();
        assertThat(repository.claim(reviewId, reviewerB, OffsetDateTime.now())).isFalse();
        assertThat(repository.get(reviewId).orElseThrow().assignedReviewerId()).isEqualTo(reviewerA);
    }

    @Test
    void consentWithdrawalRejectsPendingReviewAndAppendsAuditEvents() {
        UUID reviewId = repository.submit(repository.ownedScan(scanId, ownerId).orElseThrow(), ownerId, null, null).id();

        assertThat(repository.setConsent(scanId, ownerId, false, OffsetDateTime.now())).isTrue();

        assertThat(repository.get(reviewId).orElseThrow().status()).isEqualTo("REJECTED");
        assertThat(repository.latestStatus(scanId)).isEqualTo("REJECTED");
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM scan_training_consent_events", Integer.class)).isEqualTo(1);
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM scan_review_events WHERE event_type='CONSENT_WITHDRAWN'", Integer.class)).isEqualTo(1);
    }
}
