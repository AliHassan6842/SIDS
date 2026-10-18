package com.agrosense.recommendation.domain;

public class ChemicalSafetyGate {
    
    public boolean isChemicalTreatmentSafe(String pest, String crop, boolean isRestricted) {
        // Implement complex safety rules here
        if (isRestricted) {
            // Might need special permits, for now return false to trigger expert review
            return false;
        }
        return true;
    }
}
