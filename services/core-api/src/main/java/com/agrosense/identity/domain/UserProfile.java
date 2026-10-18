package com.agrosense.identity.domain;

import java.util.UUID;

public record UserProfile(UUID id, String email, String fullName, String language, String passwordHash) {}
