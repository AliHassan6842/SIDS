package com.agrosense.sync.infrastructure.entitysync;

import com.agrosense.sync.application.port.EntityVersionReader;
import com.agrosense.sync.domain.model.SyncEntityType;
import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * Infrastructure implementation of EntityVersionReader querying persistent table versions and timestamps.
 */
@Component
public class JdbcEntityVersionReader implements EntityVersionReader {

    private static final Set<String> ALLOWED_TABLES = Set.of(
            "observations", "samples", "tasks", "fields", "farms",
            "crop_cycles", "field_surveys", "survey_points",
            "survey_measurements", "treatments", "treatment_outcomes", "storage_objects"
    );

    private final JdbcTemplate jdbcTemplate;

    public JdbcEntityVersionReader(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public Optional<EntityStateSummary> readEntityState(String entityType, UUID entityId) {
        if (entityType == null || entityId == null) {
            return Optional.empty();
        }

        SyncEntityType syncType = SyncEntityType.fromString(entityType);
        String tableName = syncType.getTableName();

        if (!ALLOWED_TABLES.contains(tableName)) {
            return Optional.empty();
        }

        String sql = String.format("SELECT * FROM %s WHERE id = ?", tableName);

        try {
            return jdbcTemplate.query(sql, (rs) -> {
                if (rs.next()) {
                    Long version = extractVersion(rs);
                    OffsetDateTime lastModified = extractLastModified(rs);
                    return Optional.of(new EntityStateSummary(entityId, entityType, version, lastModified, true));
                }
                return Optional.empty();
            }, entityId);
        } catch (DataAccessException e) {
            // In case table or column does not exist or database is starting up
            return Optional.empty();
        }
    }

    private Long extractVersion(ResultSet rs) {
        try {
            long version = rs.getLong("version");
            return rs.wasNull() ? 0L : version;
        } catch (SQLException e) {
            return 0L;
        }
    }

    private OffsetDateTime extractLastModified(ResultSet rs) {
        try {
            Timestamp ts = rs.getTimestamp("updated_at");
            if (ts == null) {
                ts = rs.getTimestamp("created_at");
            }
            if (ts != null) {
                return ts.toInstant().atOffset(ZoneOffset.UTC);
            }
        } catch (SQLException ignored) {
            // Column may not exist on some auxiliary tables
        }
        return null;
    }
}
