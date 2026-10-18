package com.agrosense.identity.application;

import static com.agrosense.identity.api.AuthDtos.*;

import com.agrosense.identity.domain.UserProfile;
import com.agrosense.identity.infrastructure.UserRepository;
import com.agrosense.shared.error.ApiException;
import com.agrosense.shared.security.JwtService;
import java.util.Locale;
import java.util.UUID;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
    private static final String DUMMY_PASSWORD_HASH = "$2a$12$qslw4SOQEKMk4ZiyhhN91uqlSjvw8FHrPDp3lPqmJZa2DcbJTPsem";
    private final UserRepository users;
    private final PasswordEncoder passwords;
    private final JwtService jwt;
    public AuthService(UserRepository users, PasswordEncoder passwords, JwtService jwt) {
        this.users = users; this.passwords = passwords; this.jwt = jwt;
    }
    public AuthResponse register(RegisterRequest request) {
        String email = normalizeEmail(request.email());
        if (users.findByEmail(email).isPresent())
            throw new ApiException(HttpStatus.CONFLICT, "EMAIL_EXISTS", "An account already uses this email.", false);
        try {
            String language = request.language() == null ? "en" : request.language();
            return response(users.create(email, request.fullName().trim(), language, passwords.encode(request.password())));
        } catch (DuplicateKeyException e) {
            throw new ApiException(HttpStatus.CONFLICT, "EMAIL_EXISTS", "An account already uses this email.", false);
        }
    }
    public AuthResponse login(LoginRequest request) {
        var found = users.findByEmail(normalizeEmail(request.email()));
        String hash = found.map(UserProfile::passwordHash).orElse(null);
        boolean passwordMatches = passwords.matches(request.password(), hash == null ? DUMMY_PASSWORD_HASH : hash);
        if (found.isEmpty() || hash == null || !passwordMatches) throw invalidCredentials();
        UserProfile user = found.get();
        return response(user);
    }
    public UserResponse get(UUID id) { return view(users.findById(id).orElseThrow(() -> new ApiException(HttpStatus.UNAUTHORIZED, "USER_NOT_FOUND", "User is not available.", false))); }
    public UserResponse update(UUID id, UpdateProfileRequest request) { users.update(id, request.fullName().trim(), request.language()); return get(id); }
    private ApiException invalidCredentials() { return new ApiException(HttpStatus.UNAUTHORIZED, "BAD_CREDENTIALS", "Email or password is incorrect.", false); }
    private AuthResponse response(UserProfile user) { return new AuthResponse(jwt.create(user.id(), user.email()), view(user)); }
    private UserResponse view(UserProfile user) { return new UserResponse(user.id(), user.email(), user.fullName(), user.language()); }
    private String normalizeEmail(String email) { return email.trim().toLowerCase(Locale.ROOT); }
}
