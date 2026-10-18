package com.agrosense.shared.security;

import java.util.UUID;

public record CurrentUser(UUID id, String email) {
  
}
