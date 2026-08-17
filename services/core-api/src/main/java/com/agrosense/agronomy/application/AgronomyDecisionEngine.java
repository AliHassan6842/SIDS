package com.agrosense.agronomy.application;

import com.agrosense.agronomy.domain.AgronomyContext;
import com.agrosense.agronomy.domain.DecisionResult;
import com.agrosense.agronomy.domain.DecisionState;
import com.agrosense.agronomy.domain.ThresholdEvaluator;
import org.springframework.stereotype.Service;

@Service
public class AgronomyDecisionEngine {

    private final ThresholdEvaluator thresholdEvaluator;

    public AgronomyDecisionEngine(ThresholdEvaluator thresholdEvaluator) {
        this.thresholdEvaluator = thresholdEvaluator;
    }

    public DecisionResult evaluate(AgronomyContext context, Double economicThreshold) {
        if (context.pestDensity() == null) {
            return new DecisionResult(DecisionState.INSUFFICIENT_EVIDENCE, "Missing pest density data", 0.5);
        }

        if (context.hasWeatherAlert()) {
            return new DecisionResult(DecisionState.EXPERT_REVIEW, "Severe weather conditions require expert review", 0.9);
        }

        if (thresholdEvaluator.isThresholdReached(context, economicThreshold)) {
            return new DecisionResult(DecisionState.THRESHOLD_REACHED, "Pest density exceeds economic threshold", 0.95);
        }

        if (context.pestDensity() > (economicThreshold != null ? economicThreshold * 0.7 : 0)) {
            return new DecisionResult(DecisionState.MONITOR, "Pest density is approaching threshold", 0.85);
        }
        
        if (context.pestDensity() > 0) {
             return new DecisionResult(DecisionState.RESCOUT, "Low pest density detected, schedule rescouting", 0.8);
        }

        return new DecisionResult(DecisionState.NORMAL, "Conditions are normal", 1.0);
    }
}
