package com.agrosense.identity.api;

import static org.assertj.core.api.Assertions.assertThat;

import jakarta.validation.Validation;
import org.junit.jupiter.api.Test;

class AuthDtosValidationTest {
    @Test
    void rejectsOversizedLoginPasswordBeforeBcrypt() {
        try (var factory = Validation.buildDefaultValidatorFactory()) {
            var violations = factory.getValidator().validate(
                new AuthDtos.LoginRequest("farmer@example.com", "x".repeat(129)));

            assertThat(violations).anyMatch(violation -> violation.getPropertyPath().toString().equals("password"));
        }
    }
}
