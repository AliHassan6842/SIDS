package com.agrosense.identity.application;

import static com.agrosense.identity.api.AuthDtos.*;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

import com.agrosense.identity.domain.UserProfile;
import com.agrosense.identity.infrastructure.UserRepository;
import com.agrosense.shared.error.ApiException;
import com.agrosense.shared.security.JwtService;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {
    @Mock UserRepository users;
    @Mock PasswordEncoder passwords;
    @Mock JwtService jwt;
    private AuthService service;

    @BeforeEach
    void setUp() {
        service = new AuthService(users, passwords, jwt);
    }

    @Test
    void registrationNormalizesEmailHashesPasswordAndReturnsToken() {
        UUID id = UUID.randomUUID();
        UserProfile created = new UserProfile(id, "farmer@example.com", "Farmer", "ur", "encoded-password");
        when(users.findByEmail("farmer@example.com")).thenReturn(Optional.empty());
        when(passwords.encode("long-password")).thenReturn("encoded-password");
        when(users.create("farmer@example.com", "Farmer", "ur", "encoded-password")).thenReturn(created);
        when(jwt.create(id, "farmer@example.com")).thenReturn("signed-token");

        AuthResponse response = service.register(new RegisterRequest(" Farmer@Example.COM ", " Farmer ", "long-password", "ur"));

        assertThat(response.token()).isEqualTo("signed-token");
        assertThat(response.user()).isEqualTo(new UserResponse(id, "farmer@example.com", "Farmer", "ur"));
        verify(users).create("farmer@example.com", "Farmer", "ur", "encoded-password");
        verify(users, never()).create(anyString(), anyString(), anyString(), eq("long-password"));
    }

    @Test
    void registrationDefaultsLanguageToEnglishWhenOmitted() {
        UserProfile created = profile("encoded-password");
        when(users.findByEmail("farmer@example.com")).thenReturn(Optional.empty());
        when(passwords.encode("long-password")).thenReturn("encoded-password");
        when(users.create("farmer@example.com", "Farmer", "en", "encoded-password")).thenReturn(created);

        service.register(new RegisterRequest("farmer@example.com", "Farmer", "long-password", null));

        verify(users).create("farmer@example.com", "Farmer", "en", "encoded-password");
    }

    @Test
    void registrationRejectsExistingEmailWithoutHashingPassword() {
        when(users.findByEmail("farmer@example.com")).thenReturn(Optional.of(profile("encoded")));

        assertApiError(() -> service.register(new RegisterRequest("farmer@example.com", "Farmer", "long-password", null)), 409, "EMAIL_EXISTS");
        verifyNoInteractions(passwords, jwt);
    }

    @Test
    void loginVerifiesPasswordAndReturnsToken() {
        UserProfile user = profile("encoded");
        when(users.findByEmail("farmer@example.com")).thenReturn(Optional.of(user));
        when(passwords.matches("long-password", "encoded")).thenReturn(true);
        when(jwt.create(user.id(), user.email())).thenReturn("signed-token");

        AuthResponse response = service.login(new LoginRequest(" FARMER@example.com ", "long-password"));

        assertThat(response.token()).isEqualTo("signed-token");
        verify(passwords).matches("long-password", "encoded");
    }

    @Test
    void loginUsesSameErrorForUnknownEmailAndWrongPassword() {
        when(users.findByEmail("missing@example.com")).thenReturn(Optional.empty());
        assertApiError(() -> service.login(new LoginRequest("missing@example.com", "long-password")), 401, "BAD_CREDENTIALS");
        verify(passwords).matches(eq("long-password"), startsWith("$2a$12$"));

        UserProfile user = profile("encoded");
        when(users.findByEmail("farmer@example.com")).thenReturn(Optional.of(user));
        when(passwords.matches("wrong-password", "encoded")).thenReturn(false);
        assertApiError(() -> service.login(new LoginRequest("farmer@example.com", "wrong-password")), 401, "BAD_CREDENTIALS");
    }

    private UserProfile profile(String hash) {
        return new UserProfile(UUID.randomUUID(), "farmer@example.com", "Farmer", "en", hash);
    }

    private void assertApiError(org.assertj.core.api.ThrowableAssert.ThrowingCallable operation, int status, String code) {
        assertThatThrownBy(operation).isInstanceOfSatisfying(ApiException.class, exception -> {
            assertThat(exception.status().value()).isEqualTo(status);
            assertThat(exception.code()).isEqualTo(code);
        });
    }
}
