package com.agrosense.ai;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Duration;
import org.junit.jupiter.api.Test;

class AiClientSecretTest {
    @Test
    void rejectsPublishedPlaceholderToken() {
        assertThatThrownBy(() -> new AiClient("http://localhost:8000", "replace-with-at-least-24-random-characters",
            Duration.ofSeconds(1), Duration.ofSeconds(1))).isInstanceOf(IllegalStateException.class);
    }
}
