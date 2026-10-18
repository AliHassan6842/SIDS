package com.agrosense.catalog.api;

import com.agrosense.catalog.domain.PestKind;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

public final class CatalogDtos {
    private CatalogDtos() {

    }
    public record CropResponse(UUID id, String slug, String name, String imageUrl, boolean identificationSupported)
    
     {
        public CropResponse(UUID id, String slug, String name) 
        { this(id, slug, name, null, true); }
    }
    public record GuidanceResponse(String damageDescription, List<String> prevention, List<String> basicManagement,
                                   String expertAdviceNote, String sourceName, String sourceUrl, LocalDate lastVerifiedAt) {}
    public record GeneralGuidanceResponse(String harmSummary, List<String> safeRemoval,
                                          List<String> seekExpertHelpWhen, String sourceName,
                                          String sourceUrl, LocalDate lastVerifiedAt) {}
    public record PestResponse(UUID id, String slug, PestKind kind, String commonName, String scientificName, String description,
                               List<CropResponse> affectedCrops, GuidanceResponse guidance,
                               GeneralGuidanceResponse generalGuidance, String imageUrl) {
        public PestResponse(UUID id, String slug, String commonName, String scientificName, String description,
                            List<CropResponse> affectedCrops, GuidanceResponse guidance) {
            this(id, slug, PestKind.CROP_PEST, commonName, scientificName, description, affectedCrops, guidance, null, null);
        }
    }
}
