package com.agrosense.promotion.infrastructure;

import static com.agrosense.promotion.api.PromotionDtos.*;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class PromotionRepository {
    private final JdbcTemplate jdbc;

    public PromotionRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public PromotionResponse insert(UUID id, PromotionRequest request, UUID promotedBy, OffsetDateTime promotedAt) {
        jdbc.update("INSERT INTO model_promotions(id,model_id,model_version,dataset_version,manifest_sha256,artifact_sha256,supersedes_promotion_id,promoted_by,promoted_at) VALUES (?,?,?,?,?,?,?,?,?)",
            id, request.modelId(), request.modelVersion(), request.datasetVersion(), request.manifestSha256(),
            request.artifactSha256(), request.supersedesPromotionId(), promotedBy, promotedAt);
        for (UUID reviewId : request.reviewIds()) {
            jdbc.update("INSERT INTO model_promotion_reviews(promotion_id,review_id) VALUES (?,?)", id, reviewId);
        }
        return get(id).orElseThrow();
    }

    public Optional<PromotionResponse> get(UUID id) {
        var rows = jdbc.query("SELECT id,model_id,model_version,dataset_version,manifest_sha256,artifact_sha256,supersedes_promotion_id,promoted_by,promoted_at FROM model_promotions WHERE id=?",
            this::promotion, id);
        if (rows.isEmpty()) return Optional.empty();
        PromotionResponse row = rows.getFirst();
        List<UUID> reviewIds = jdbc.query("SELECT review_id FROM model_promotion_reviews WHERE promotion_id=? ORDER BY review_id",
            (rs, number) -> rs.getObject(1, UUID.class), id);
        return Optional.of(new PromotionResponse(row.id(), row.modelId(), row.modelVersion(), row.datasetVersion(),
            row.manifestSha256(), row.artifactSha256(), row.supersedesPromotionId(), reviewIds,
            row.promotedBy(), row.promotedAt()));
    }

    private PromotionResponse promotion(ResultSet rs, int row) throws SQLException {
        return new PromotionResponse(rs.getObject("id", UUID.class), rs.getString("model_id"),
            rs.getString("model_version"), rs.getString("dataset_version"), rs.getString("manifest_sha256"),
            rs.getString("artifact_sha256"), rs.getObject("supersedes_promotion_id", UUID.class), List.of(),
            rs.getObject("promoted_by", UUID.class), rs.getObject("promoted_at", OffsetDateTime.class));
    }
}
