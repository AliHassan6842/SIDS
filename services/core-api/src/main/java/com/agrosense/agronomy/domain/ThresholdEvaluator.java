package com.agrosense.agronomy.domain;

public class ThresholdEvaluator {
    
    public boolean isThresholdReached(AgronomyContext context, Double economicThreshold) {
        if (context.pestDensity() == null || economicThreshold == null) {
            return false;
        }
        return context.pestDensity() >= economicThreshold || (context.cropDamagePercentage() != null && context.cropDamagePercentage() > 15.0);
    }
}
