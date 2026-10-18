package com.agrosense.ai;

public final class AiContracts {
    private AiContracts() {}
    public record Quality(String brightness, String blur, String subjectSize) {}
    public record ValidateResponse(boolean valid, String reason, boolean insectCandidate, Quality quality) {}
    public record BoundingBox(double x, double y, double width, double height) {}
    public record Prediction(String pestId, double confidence, BoundingBox bbox) {}
    public record Model(String id, String version, String datasetVersion) {}
    public record IdentifyResponse(String status, String reason, Prediction prediction, Model model) {}
}
