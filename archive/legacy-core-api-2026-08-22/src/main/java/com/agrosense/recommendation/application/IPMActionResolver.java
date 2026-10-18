package com.agrosense.recommendation.application;

import com.agrosense.agronomy.domain.DecisionState;
import com.agrosense.recommendation.domain.ChemicalSafetyGate;
import com.agrosense.recommendation.domain.Recommendation;
import com.agrosense.recommendation.domain.RecommendationPolicy;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

@Service
public class IPMActionResolver {

    private final ChemicalSafetyGate chemicalSafetyGate;

    public IPMActionResolver(ChemicalSafetyGate chemicalSafetyGate) {
        this.chemicalSafetyGate = chemicalSafetyGate;
    }

    public Recommendation resolveAction(DecisionState state, String pest, String crop, boolean hasRestrictedChemicals) {
        return switch (state) {
            case NORMAL -> new Recommendation("No Action Required", "Continue standard practices.", RecommendationPolicy.NO_ACTION, Collections.emptyList());
            case MONITOR -> new Recommendation("Monitor closely", "Pest presence detected, monitor the situation.", RecommendationPolicy.MONITOR, Collections.emptyList());
            case RESCOUT -> new Recommendation("Rescout", "Schedule another scouting session soon.", RecommendationPolicy.RESCOUT, Collections.emptyList());
            case INSUFFICIENT_EVIDENCE -> new Recommendation("Expert Review Required", "Not enough data to make a decision.", RecommendationPolicy.EXPERT_REVIEW, Collections.emptyList());
            case EXPERT_REVIEW -> new Recommendation("Expert Review Required", "Complex situation requires agronomist.", RecommendationPolicy.EXPERT_REVIEW, Collections.emptyList());
            case THRESHOLD_REACHED -> {
                if (chemicalSafetyGate.isChemicalTreatmentSafe(pest, crop, hasRestrictedChemicals)) {
                    yield new Recommendation("Apply Chemical Treatment", "Threshold reached, safe to apply chemicals.", RecommendationPolicy.CHEMICAL_OPTION, Collections.emptyList());
                } else {
                    yield new Recommendation("Expert Review Required", "Threshold reached but chemical safety check failed.", RecommendationPolicy.EXPERT_REVIEW, Collections.emptyList());
                }
            }
        };
    }
}
