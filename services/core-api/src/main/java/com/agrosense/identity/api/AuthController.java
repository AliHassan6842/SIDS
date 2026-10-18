package com.agrosense.identity.api;

import static com.agrosense.identity.api.AuthDtos.*;

import com.agrosense.identity.application.AuthService;
import com.agrosense.shared.security.CurrentUser;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class AuthController {
    private final AuthService auth;
    public AuthController(AuthService auth) { this.auth = auth; }
    @PostMapping("/auth/register") @ResponseStatus(HttpStatus.CREATED)
    public AuthResponse register(@Valid @RequestBody RegisterRequest request) { return auth.register(request); }
    @PostMapping("/auth/login")
    public AuthResponse login(@Valid @RequestBody LoginRequest request) { return auth.login(request); }
    @GetMapping("/me")
    public UserResponse me(@AuthenticationPrincipal CurrentUser user) { return auth.get(user.id()); }
    @PutMapping("/me")
    public UserResponse update(@AuthenticationPrincipal CurrentUser user, @Valid @RequestBody UpdateProfileRequest request) {
        return auth.update(user.id(), request);
    }
}
