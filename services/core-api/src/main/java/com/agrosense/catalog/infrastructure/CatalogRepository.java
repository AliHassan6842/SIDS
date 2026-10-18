package com.agrosense.catalog.infrastructure;

import static com.agrosense.catalog.api.CatalogDtos.*;

import com.agrosense.catalog.domain.PestKind;
import com.agrosense.shared.error.ApiException;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class CatalogRepository {
    private final JdbcTemplate jdbc;
    public CatalogRepository(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    public List<CropResponse> crops() {
        return crops(false);
    }
    public List<CropResponse> crops(boolean includeUnavailable) {
        String sql = "SELECT id,slug,name,image_url,identification_supported FROM crops WHERE supported=TRUE";
        
        if (!includeUnavailable) sql += " AND identification_supported=TRUE";
        return jdbc.query(sql + " ORDER BY name", this::crop);
    }
    public Optional<CropResponse> cropById(UUID id) {
        return jdbc.query("SELECT id,slug,name,image_url,identification_supported FROM crops WHERE supported=TRUE AND identification_supported=TRUE AND id=?", this::crop, id).stream().findFirst();
    }
    public List<PestResponse> pests(UUID cropId) {
        return pests(cropId == null ? null : PestKind.CROP_PEST, cropId);
    }
    public List<PestResponse> pests(PestKind kind, UUID cropId) {
        String select = "SELECT DISTINCT p.id,p.slug,p.pest_kind,p.common_name,p.scientific_name,p.description,p.image_url FROM pests p "
            + "LEFT JOIN crop_pests cp ON cp.pest_id=p.id LEFT JOIN crops c ON c.id=cp.crop_id "
            + "WHERE p.supported=TRUE";
        List<Object> parameters = new ArrayList<>();
        if (kind != null) { select += " AND p.pest_kind=?"; parameters.add(kind.name()); }
        if (cropId != null) { select += " AND c.id=?"; parameters.add(cropId); }
        return jdbc.query(select + " ORDER BY p.common_name", (rs, row) -> pestSummary(rs), parameters.toArray());
    }
    public PestResponse pest(UUID id) {
        return detailedPest("id", id);
    }
    public PestResponse pestBySlug(String slug) {
        return detailedPest("slug", slug);
    }
    private PestResponse detailedPest(String field, Object value) {
        var rows = jdbc.query("SELECT id,slug,pest_kind,common_name,scientific_name,description,image_url FROM pests WHERE supported=TRUE AND " + field + "=?",
            (rs, row) -> pestSummary(rs), value);
        if (rows.isEmpty()) throw new ApiException(HttpStatus.NOT_FOUND, "PEST_NOT_FOUND", "Supported pest was not found.", false);
        PestResponse pest = rows.getFirst();
        if (pest.kind() == PestKind.GENERAL_INSECT) {
            var guidance = jdbc.query("SELECT harm_summary,safe_removal,seek_expert_help_when,source_name,source_url,last_verified_at FROM general_insect_guidance WHERE pest_id=?",
                (rs, row) -> new GeneralGuidanceResponse(rs.getString(1), lines(rs.getString(2)), lines(rs.getString(3)),
                    rs.getString(4), rs.getString(5), rs.getObject(6, java.time.LocalDate.class)), pest.id());
            return new PestResponse(pest.id(), pest.slug(), pest.kind(), pest.commonName(), pest.scientificName(),
                pest.description(), List.of(), null, guidance.stream().findFirst().orElse(null), pest.imageUrl());
        }
        List<CropResponse> crops = jdbc.query("SELECT c.id,c.slug,c.name,c.image_url,c.identification_supported FROM crops c JOIN crop_pests cp ON cp.crop_id=c.id WHERE cp.pest_id=? AND c.supported=TRUE ORDER BY c.name", this::crop, pest.id());
        var guidance = jdbc.query("SELECT damage_description,prevention,basic_management,expert_advice_note,source_name,source_url,last_verified_at FROM pest_guidance WHERE pest_id=?",
            (rs, row) -> new GuidanceResponse(rs.getString(1), lines(rs.getString(2)), lines(rs.getString(3)), rs.getString(4), rs.getString(5), rs.getString(6), rs.getObject(7, java.time.LocalDate.class)), pest.id());
        return new PestResponse(pest.id(), pest.slug(), pest.kind(), pest.commonName(), pest.scientificName(), pest.description(), crops, guidance.stream().findFirst().orElse(null), null, pest.imageUrl());
    }
    public boolean supports(UUID cropId, String pestSlug) {
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM crop_pests cp JOIN pests p ON p.id=cp.pest_id WHERE cp.crop_id=? AND p.slug=? AND p.supported=TRUE", Integer.class, cropId, pestSlug);
        return count != null && count > 0;
    }
    public UUID pestId(String slug) {
        List<UUID> ids = jdbc.query("SELECT id FROM pests WHERE slug=? AND supported=TRUE", (rs, row) -> rs.getObject(1, UUID.class), slug);
        return ids.isEmpty() ? null : ids.getFirst();
    }
    public UUID generalInsectId(String slug) {
        List<UUID> ids = jdbc.query("SELECT id FROM pests WHERE slug=? AND supported=TRUE AND pest_kind='GENERAL_INSECT'",
            (rs, row) -> rs.getObject(1, UUID.class), slug);
        return ids.isEmpty() ? null : ids.getFirst();
    }
    private CropResponse crop(ResultSet rs, int row) throws SQLException { return new CropResponse(rs.getObject("id", UUID.class), rs.getString("slug"), rs.getString("name"), rs.getString("image_url"), rs.getBoolean("identification_supported")); }
    private PestResponse pestSummary(ResultSet rs) throws SQLException { return new PestResponse(rs.getObject("id", UUID.class), rs.getString("slug"), PestKind.valueOf(rs.getString("pest_kind")), rs.getString("common_name"), rs.getString("scientific_name"), rs.getString("description"), List.of(), null, null, rs.getString("image_url")); }
    private List<String> lines(String value) { return Arrays.stream(value.split("\\r?\\n")).map(String::trim).filter(s -> !s.isEmpty()).toList(); }
}
