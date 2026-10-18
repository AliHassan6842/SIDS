package com.agrosense.review.infrastructure;

import static com.agrosense.review.api.ReviewDtos.ReviewResponse;

import com.agrosense.scan.domain.IdentificationMode;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class ReviewRepository {
    public record ScanIntake(UUID id, UUID ownerId, IdentificationMode mode, String status,
                             boolean trainingConsent, OffsetDateTime consentedAt, String imageKey) {}

    private final JdbcTemplate jdbc;

    public ReviewRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public Optional<ScanIntake> ownedScan(UUID scanId, UUID ownerId) {
        return jdbc.query("SELECT id,user_id,identification_mode,status,training_consent,consented_at,image_key FROM scans WHERE id=? AND user_id=?",
            this::scan, scanId, ownerId).stream().findFirst();
    }

    public String latestStatus(UUID scanId) {
        return jdbc.query("SELECT status FROM scan_reviews WHERE scan_id=? ORDER BY created_at DESC LIMIT 1",
            (rs, row) -> rs.getString(1), scanId).stream().findFirst().orElse("NOT_SUBMITTED");
    }

    public boolean setConsent(UUID scanId, UUID ownerId, boolean consented, OffsetDateTime changedAt) {
        int updated = jdbc.update("UPDATE scans SET training_consent=?,consented_at=? WHERE id=? AND user_id=? AND training_consent<>?",
            consented, consented ? changedAt : null, scanId, ownerId, consented);
        if (updated == 0) return false;
        jdbc.update("INSERT INTO scan_training_consent_events(id,scan_id,actor_user_id,consented,created_at) VALUES (?,?,?,?,?)",
            UUID.randomUUID(), scanId, ownerId, consented, changedAt);
        if (!consented) rejectPendingOnWithdrawal(scanId, ownerId, changedAt);
        return true;
    }

    public void recordInitialConsent(UUID scanId, UUID ownerId, OffsetDateTime createdAt) {
        jdbc.update("INSERT INTO scan_training_consent_events(id,scan_id,actor_user_id,consented,created_at) VALUES (?,?,?,?,?)",
            UUID.randomUUID(), scanId, ownerId, true, createdAt);
    }

    public ReviewResponse submit(ScanIntake scan, UUID ownerId, String proposedLabelSlug, String notes) {
        UUID id = UUID.randomUUID();
        OffsetDateTime now = OffsetDateTime.now();
        jdbc.update("INSERT INTO scan_reviews(id,scan_id,submitted_by,proposed_label_slug,submission_notes,status,created_at) VALUES (?,?,?,?,?,'PENDING',?)",
            id, scan.id(), ownerId, proposedLabelSlug, notes, now);
        event(id, ownerId, "SUBMITTED", now);
        return get(id).orElseThrow();
    }

    public List<ReviewResponse> queue(String status) {
        return jdbc.query(baseSql() + " WHERE r.status=? ORDER BY r.created_at", this::review, status);
    }

    public Optional<ReviewResponse> get(UUID reviewId) {
        return jdbc.query(baseSql() + " WHERE r.id=?", this::review, reviewId).stream().findFirst();
    }

    public boolean claim(UUID reviewId, UUID reviewerId, OffsetDateTime claimedAt) {
        int updated = jdbc.update("UPDATE scan_reviews SET assigned_reviewer_id=?,claimed_at=? WHERE id=? AND status='PENDING' AND assigned_reviewer_id IS NULL",
            reviewerId, claimedAt, reviewId);
        if (updated == 1) event(reviewId, reviewerId, "CLAIMED", claimedAt);
        return updated == 1;
    }

    public boolean decide(UUID reviewId, UUID reviewerId, String decision, String labelSlug,
                          String notes, OffsetDateTime reviewedAt) {
        int updated = jdbc.update("UPDATE scan_reviews SET status=?,reviewer_label_slug=?,reviewer_notes=?,reviewed_at=? WHERE id=? AND status='PENDING' AND assigned_reviewer_id=?",
            decision, labelSlug, notes, reviewedAt, reviewId, reviewerId);
        if (updated == 1) event(reviewId, reviewerId, decision, reviewedAt);
        return updated == 1;
    }

    public Optional<String> assignedImageKey(UUID reviewId, UUID reviewerId, boolean admin) {
        String sql = "SELECT s.image_key FROM scan_reviews r JOIN scans s ON s.id=r.scan_id WHERE r.id=?";
        if (!admin) sql += " AND r.assigned_reviewer_id=?";
        Object[] args = admin ? new Object[]{reviewId} : new Object[]{reviewId, reviewerId};
        return jdbc.query(sql, (rs, row) -> rs.getString(1), args).stream().findFirst();
    }

    public boolean approvedAndConsented(UUID reviewId) {
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM scan_reviews r JOIN scans s ON s.id=r.scan_id WHERE r.id=? AND r.status='APPROVED' AND s.training_consent=TRUE",
            Integer.class, reviewId);
        return count != null && count == 1;
    }

    private void rejectPendingOnWithdrawal(UUID scanId, UUID actorId, OffsetDateTime at) {
        List<UUID> ids = jdbc.query("SELECT id FROM scan_reviews WHERE scan_id=? AND status='PENDING'",
            (rs, row) -> rs.getObject(1, UUID.class), scanId);
        for (UUID id : ids) {
            jdbc.update("UPDATE scan_reviews SET status='REJECTED',reviewer_notes='Training consent withdrawn by owner.',reviewed_at=? WHERE id=? AND status='PENDING'", at, id);
            event(id, actorId, "CONSENT_WITHDRAWN", at);
        }
    }

    private void event(UUID reviewId, UUID actorId, String type, OffsetDateTime at) {
        jdbc.update("INSERT INTO scan_review_events(id,review_id,actor_user_id,event_type,created_at) VALUES (?,?,?,?,?)",
            UUID.randomUUID(), reviewId, actorId, type, at);
    }

    private String baseSql() {
        return "SELECT r.id,r.scan_id,r.submitted_by,s.identification_mode,s.status scan_status,r.proposed_label_slug,r.submission_notes,r.status,r.assigned_reviewer_id,r.reviewer_label_slug,r.reviewer_notes,r.claimed_at,r.reviewed_at,r.created_at FROM scan_reviews r JOIN scans s ON s.id=r.scan_id";
    }

    private ScanIntake scan(ResultSet rs, int row) throws SQLException {
        return new ScanIntake(rs.getObject("id", UUID.class), rs.getObject("user_id", UUID.class),
            IdentificationMode.valueOf(rs.getString("identification_mode")), rs.getString("status"),
            rs.getBoolean("training_consent"), rs.getObject("consented_at", OffsetDateTime.class), rs.getString("image_key"));
    }

    private ReviewResponse review(ResultSet rs, int row) throws SQLException {
        return new ReviewResponse(rs.getObject("id", UUID.class), rs.getObject("scan_id", UUID.class),
            rs.getObject("submitted_by", UUID.class), IdentificationMode.valueOf(rs.getString("identification_mode")),
            rs.getString("scan_status"), rs.getString("proposed_label_slug"), rs.getString("submission_notes"),
            rs.getString("status"), rs.getObject("assigned_reviewer_id", UUID.class), rs.getString("reviewer_label_slug"),
            rs.getString("reviewer_notes"), rs.getObject("claimed_at", OffsetDateTime.class),
            rs.getObject("reviewed_at", OffsetDateTime.class), rs.getObject("created_at", OffsetDateTime.class));
    }
}
