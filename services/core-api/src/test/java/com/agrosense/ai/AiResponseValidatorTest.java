package com.agrosense.ai;

import static com.agrosense.ai.AiContracts.*;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.agrosense.shared.error.ApiException;
import org.junit.jupiter.api.Test;

class AiResponseValidatorTest {
    private final AiResponseValidator validator = new AiResponseValidator();

    @Test
    void acceptsWellFormedIdentifiedResponse() {
        IdentifyResponse response = identified(0.91, new BoundingBox(0.1, 0.2, 0.3, 0.4));

        assertThat(validator.validate(response)).isSameAs(response);
    }

    @Test
    void acceptsUnknownWithoutPrediction() {
        IdentifyResponse response = new IdentifyResponse("UNKNOWN", "LOW_CONFIDENCE", null, model());

        assertThat(validator.validate(response)).isSameAs(response);
    }

    @Test
    void rejectsUnexpectedStatus() {
        assertInvalid(new IdentifyResponse("FAILED", null, null, model()));
    }

    @Test
    void rejectsIdentifiedResponseWithoutModel() {
        IdentifyResponse response = identified(0.91, null);
        response = new IdentifyResponse(response.status(), response.reason(), response.prediction(), null);

        assertInvalid(response);
    }

    @Test
    void rejectsNonFiniteOrOutOfRangeConfidence() {
        assertInvalid(identified(Double.NaN, null));
        assertInvalid(identified(1.01, null));
    }

    @Test
    void rejectsOutOfFrameBoundingBox() {
        assertInvalid(identified(0.91, new BoundingBox(0.8, 0.2, 0.3, 0.4)));
        assertInvalid(identified(0.91, new BoundingBox(0.1, 0.2, 0.0, 0.4)));
    }

    @Test
    void rejectsNearestClassLeakOnUnknownResponse() {
        IdentifyResponse response = new IdentifyResponse("UNKNOWN", "LOW_CONFIDENCE",
            new Prediction("rice-leaf-roller", 0.4, null), model());

        assertInvalid(response);
    }

    @Test
    void rejectsStatusReasonAndModelMetadataMismatches() {
        assertInvalid(new IdentifyResponse("IDENTIFIED", "LOW_CONFIDENCE",
            new Prediction("rice-leaf-roller", 0.9, null), model()));
        assertInvalid(new IdentifyResponse("UNKNOWN", "TOO_BLURRY", null, model()));
        assertInvalid(new IdentifyResponse("REJECTED_IMAGE", "NO_DETECTION", null, model()));
        assertInvalid(new IdentifyResponse("UNKNOWN", "NO_DETECTION", null, null));
        assertInvalid(new IdentifyResponse("UNKNOWN", "NO_DETECTION", null,
            new Model("detector", "1.0", "")));
    }

    @Test
    void rejectsMalformedPestIdentifier() {
        assertInvalid(new IdentifyResponse("IDENTIFIED", null,
            new Prediction("Rice Leaf Roller", 0.9, null), model()));
    }

    @Test
    void validatesFrameResponseShapeAndStateConsistency() {
        ValidateResponse ready = new ValidateResponse(true, null, true, new Quality("OK", "OK", "OK"));
        assertThat(validator.validate(ready)).isSameAs(ready);
        assertThatThrownBy(() -> validator.validate(new ValidateResponse(true, "TOO_BLURRY", true,
            new Quality("OK", "OK", "OK")))).isInstanceOf(ApiException.class);
        assertThatThrownBy(() -> validator.validate(new ValidateResponse(false, "TOO_BLURRY", true,
            new Quality("OK", "HIGH", "OK")))).isInstanceOf(ApiException.class);
    }

    private IdentifyResponse identified(double confidence, BoundingBox box) {
        return new IdentifyResponse("IDENTIFIED", null,
            new Prediction("rice-leaf-roller", confidence, box),
            model());
    }

    private Model model() { return new Model("rice-pest-classifier", "1.0", "ip102-rice-v1"); }

    private void assertInvalid(IdentifyResponse response) {
        assertThatThrownBy(() -> validator.validate(response))
            .isInstanceOfSatisfying(ApiException.class, exception -> {
                assertThat(exception.code()).isEqualTo("AI_RESPONSE_INVALID");
                assertThat(exception.status().value()).isEqualTo(503);
            });
    }
}
