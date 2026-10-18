package com.agrosense.scan.infrastructure;

import static com.agrosense.ai.AiContracts.*;

import com.agrosense.scan.domain.IdentificationMode;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class ScanRepository {
    public record Row(UUID id, UUID userId, IdentificationMode mode, UUID cropId, String cropSlug, String cropName,
                      String cropImageUrl, boolean cropIdentificationSupported, String imageKey,
                      String status, OffsetDateTime createdAt, String pestSlug, Double confidence, BoundingBox bbox,
                      String modelId, String modelVersion, String datasetVersion, String reason,
                      boolean trainingConsent, OffsetDateTime consentedAt, String reviewStatus) {}
    private final JdbcTemplate jdbc;
    public ScanRepository(JdbcTemplate jdbc) { this.jdbc = jdbc; }
    public void insert(UUID scanId, UUID userId, IdentificationMode mode, UUID cropId, String imageKey,
                       boolean trainingConsent, IdentifyResponse ai, UUID pestId) {
        OffsetDateTime now = OffsetDateTime.now();
        jdbc.update("INSERT INTO scans(id,user_id,identification_mode,crop_id,image_key,status,training_consent,consented_at,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            scanId, userId, mode.name(), cropId, imageKey, ai.status(), trainingConsent, trainingConsent ? now : null, now);
        if (trainingConsent) {
            jdbc.update("INSERT INTO scan_training_consent_events(id,scan_id,actor_user_id,consented,created_at) VALUES (?,?,?,?,?)",
                UUID.randomUUID(), scanId, userId, true, now);
        }
        Prediction prediction = ai.prediction();
        BoundingBox box = prediction == null ? null : prediction.bbox();
        Model model = ai.model();
        jdbc.update("INSERT INTO scan_predictions(scan_id,pest_id,confidence,bbox_x,bbox_y,bbox_width,bbox_height,model_id,model_version,dataset_version,result_type,reason) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            scanId, pestId, prediction == null ? null : prediction.confidence(), box == null ? null : box.x(),
            box == null ? null : box.y(), box == null ? null : box.width(), box == null ? null : box.height(),
            model == null ? null : model.id(), model == null ? null : model.version(),
            model == null ? null : model.datasetVersion(), ai.status(), ai.reason());
    }
    public List<Row> list(UUID userId) { return jdbc.query(baseSql() + " WHERE s.user_id=? ORDER BY s.created_at DESC", this::map, userId); }
    public Optional<Row> get(UUID scanId, UUID userId) { return jdbc.query(baseSql() + " WHERE s.id=? AND s.user_id=?", this::map, scanId, userId).stream().findFirst(); }
    private String baseSql() {
        return "SELECT s.id,s.user_id,s.identification_mode,s.crop_id,c.slug crop_slug,c.name crop_name,c.image_url crop_image_url,c.identification_supported crop_identification_supported,s.image_key,s.status,s.created_at,p.slug pest_slug,sp.confidence,sp.bbox_x,sp.bbox_y,sp.bbox_width,sp.bbox_height,sp.model_id,sp.model_version,sp.dataset_version,sp.reason,s.training_consent,s.consented_at,COALESCE((SELECT sr.status FROM scan_reviews sr WHERE sr.scan_id=s.id ORDER BY sr.created_at DESC LIMIT 1),'NOT_SUBMITTED') review_status FROM scans s LEFT JOIN crops c ON c.id=s.crop_id JOIN scan_predictions sp ON sp.scan_id=s.id LEFT JOIN pests p ON p.id=sp.pest_id";
    }
    private Row map(ResultSet rs, int row) throws SQLException {
        Double width = nullableDouble(rs, "bbox_width");
        BoundingBox bbox = width == null ? null : new BoundingBox(rs.getDouble("bbox_x"), rs.getDouble("bbox_y"), width, rs.getDouble("bbox_height"));
        return new Row(rs.getObject("id", UUID.class), rs.getObject("user_id", UUID.class), IdentificationMode.valueOf(rs.getString("identification_mode")), rs.getObject("crop_id", UUID.class),
            rs.getString("crop_slug"), rs.getString("crop_name"), rs.getString("crop_image_url"), rs.getBoolean("crop_identification_supported"), rs.getString("image_key"), rs.getString("status"),
            rs.getObject("created_at", OffsetDateTime.class), rs.getString("pest_slug"), nullableDouble(rs, "confidence"), bbox,
            rs.getString("model_id"), rs.getString("model_version"), rs.getString("dataset_version"), rs.getString("reason"),
            rs.getBoolean("training_consent"), rs.getObject("consented_at", OffsetDateTime.class), rs.getString("review_status"));
    }
    private Double nullableDouble(ResultSet rs, String column) throws SQLException { double value = rs.getDouble(column); return rs.wasNull() ? null : value; }
}
