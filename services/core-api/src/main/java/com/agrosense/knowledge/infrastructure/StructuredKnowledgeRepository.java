package com.agrosense.knowledge.infrastructure;

import com.agrosense.knowledge.domain.EconomicThresholdRecord;
import com.agrosense.knowledge.domain.PesticideRegistrationRecord;
import com.agrosense.knowledge.domain.ScoutingGuidanceRecord;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class StructuredKnowledgeRepository {

    private final JdbcClient jdbcClient;

    public StructuredKnowledgeRepository(JdbcClient jdbcClient) {
        this.jdbcClient = jdbcClient;
    }

    public List<EconomicThresholdRecord> findEconomicThresholds(String crop, String pest) {
        return jdbcClient.sql("SELECT id, crop, pest, threshold_value as thresholdValue, unit, description FROM knowledge.economic_thresholds WHERE crop = :crop AND pest = :pest")
                .param("crop", crop)
                .param("pest", pest)
                .query(EconomicThresholdRecord.class)
                .list();
    }

    public List<ScoutingGuidanceRecord> findScoutingGuidance(String crop, String pest) {
        return jdbcClient.sql("SELECT id, crop, pest, growth_stage as growthStage, scouting_method as scoutingMethod, description FROM knowledge.scouting_guidance WHERE crop = :crop AND pest = :pest")
                .param("crop", crop)
                .param("pest", pest)
                .query(ScoutingGuidanceRecord.class)
                .list();
    }

    public List<PesticideRegistrationRecord> findPesticideRegistrations(String targetPest) {
        return jdbcClient.sql("SELECT id, product_name as productName, active_ingredient as activeIngredient, target_pest as targetPest, registration_number as registrationNumber, is_restricted as isRestricted FROM knowledge.pesticide_registrations WHERE target_pest = :pest")
                .param("pest", targetPest)
                .query(PesticideRegistrationRecord.class)
                .list();
    }
}
