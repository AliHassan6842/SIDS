package com.agrosense.knowledge.domain;

public record PesticideRegistrationRecord(
    Long id,
    String productName,
    String activeIngredient,
    String targetPest,
    String registrationNumber,
    Boolean isRestricted
) {}
