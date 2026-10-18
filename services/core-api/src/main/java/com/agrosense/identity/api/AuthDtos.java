package com.agrosense.identity.api;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.util.UUID;

public final class AuthDtos {
    private AuthDtos() {}
    public record RegisterRequest(@Email @NotBlank String email, @NotBlank @Size(min=2,max=120) String fullName,
                                  @NotBlank @Size(min=10,max=128) String password,
                                  @Pattern(regexp="^[a-z]{2}(?:-[A-Z]{2})?$") String language) {}
    public record LoginRequest(@Email @NotBlank String email, @NotBlank @Size(max=128) String password) {}
    public record UserResponse(UUID id, String email, String fullName, String language) {}
    public record AuthResponse(String token, UserResponse user) {}
    public record UpdateProfileRequest(@NotBlank @Size(min=2,max=120) String fullName,
                                       @Pattern(regexp="^[a-z]{2}(?:-[A-Z]{2})?$") String language) {}
}
