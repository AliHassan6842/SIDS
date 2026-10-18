package com.agrosense.ai;

import static com.agrosense.ai.AiContracts.*;

import com.agrosense.shared.error.ApiException;
import java.util.Set;
import java.util.regex.Pattern;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

@Component
public class AiResponseValidator {
    private static final Set<String> ALLOWED_STATUSES = Set.of("IDENTIFIED", "UNKNOWN", "REJECTED_IMAGE");
    private static final Set<String> UNKNOWN_REASONS = Set.of("LOW_CONFIDENCE", "NO_DETECTION", "CLASS_UNCERTAIN", "MODEL_UNAVAILABLE");
    private static final Set<String> REJECTION_REASONS = Set.of("TOO_DARK", "TOO_BRIGHT", "TOO_BLURRY", "SUBJECT_TOO_SMALL", "NO_INSECT_CANDIDATE", "INVALID_IMAGE");
    private static final Set<String> BRIGHTNESS_BANDS = Set.of("LOW", "OK", "HIGH");
    private static final Set<String> BLUR_BANDS = Set.of("LOW", "OK");
    private static final Set<String> SUBJECT_BANDS = Set.of("LOW", "OK", "UNKNOWN");
    private static final Pattern PEST_ID = Pattern.compile("^[a-z0-9]+(?:-[a-z0-9]+)*$");

    public IdentifyResponse validate(IdentifyResponse response) {
        if (response == null || !ALLOWED_STATUSES.contains(response.status())) throw invalid();
        validateModel(response.model());
        switch (response.status()) {
            case "IDENTIFIED" -> validateIdentified(response);
            case "UNKNOWN" -> validateNonIdentified(response, UNKNOWN_REASONS);
            case "REJECTED_IMAGE" -> validateNonIdentified(response, REJECTION_REASONS);
            default -> throw invalid();
        }
        return response;
    }

    public ValidateResponse validate(ValidateResponse response) {
        if (response == null || response.quality() == null) throw invalid();
        Quality quality = response.quality();
        if (!BRIGHTNESS_BANDS.contains(quality.brightness()) || !BLUR_BANDS.contains(quality.blur())
            || !SUBJECT_BANDS.contains(quality.subjectSize())) throw invalid();
        if (response.valid()) {
            if (response.reason() != null || !response.insectCandidate()) throw invalid();
        } else if (!REJECTION_REASONS.contains(response.reason())) throw invalid();
        return response;
    }

    private void validateIdentified(IdentifyResponse response) {
        Prediction prediction = response.prediction();
        if (response.reason() != null || prediction == null || !PEST_ID.matcher(nullToEmpty(prediction.pestId())).matches()) throw invalid();
        if (!unitInterval(prediction.confidence())) throw invalid();
        if (prediction.bbox() != null) validateBox(prediction.bbox());
    }

    private void validateNonIdentified(IdentifyResponse response, Set<String> allowedReasons) {
        if (response.prediction() != null || !allowedReasons.contains(response.reason())) throw invalid();
    }

    private void validateModel(Model model) {
        if (model == null || blank(model.id()) || blank(model.version()) || blank(model.datasetVersion())) throw invalid();
    }

    private void validateBox(BoundingBox box) {
        if (!unitInterval(box.x()) || !unitInterval(box.y()) || !positiveUnit(box.width()) || !positiveUnit(box.height())
            || box.x() + box.width() > 1.0 || box.y() + box.height() > 1.0) throw invalid();
    }

    private boolean unitInterval(double value) { return Double.isFinite(value) && value >= 0.0 && value <= 1.0; }
    private boolean positiveUnit(double value) { return Double.isFinite(value) && value > 0.0 && value <= 1.0; }
    private boolean blank(String value) { return value == null || value.isBlank(); }
    private String nullToEmpty(String value) { return value == null ? "" : value; }
    private ApiException invalid() {
        return new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "AI_RESPONSE_INVALID",
            "Identification service returned an invalid response.", true);
    }
}
