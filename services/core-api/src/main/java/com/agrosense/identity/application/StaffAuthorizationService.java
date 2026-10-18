package com.agrosense.identity.application;

import com.agrosense.identity.domain.SystemRole;
import com.agrosense.identity.infrastructure.UserRepository;
import com.agrosense.shared.error.ApiException;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

@Service
public class StaffAuthorizationService {
    private final UserRepository users;

    public StaffAuthorizationService(UserRepository users) {
        this.users = users;
    }

    public SystemRole requireReviewer(UUID userId) {
        SystemRole role = role(userId);
        if (role != SystemRole.REVIEWER && role != SystemRole.ADMIN) throw forbidden();
        return role;
    }

    public void requireAdmin(UUID userId) {
        if (role(userId) != SystemRole.ADMIN) throw forbidden();
    }

    private SystemRole role(UUID userId) {
        return users.systemRole(userId).orElseThrow(this::forbidden);
    }

    private ApiException forbidden() {
        return new ApiException(HttpStatus.FORBIDDEN, "STAFF_ACCESS_REQUIRED",
            "This operation requires assigned staff access.", false);
    }
}
