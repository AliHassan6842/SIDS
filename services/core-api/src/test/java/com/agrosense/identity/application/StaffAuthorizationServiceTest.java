package com.agrosense.identity.application;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

import com.agrosense.identity.domain.SystemRole;
import com.agrosense.identity.infrastructure.UserRepository;
import com.agrosense.shared.error.ApiException;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class StaffAuthorizationServiceTest {
    private final UserRepository users = mock(UserRepository.class);
    private final StaffAuthorizationService service = new StaffAuthorizationService(users);

    @Test
    void ordinaryUserCannotReadReviewQueue() {
        UUID userId = UUID.randomUUID();
        when(users.systemRole(userId)).thenReturn(Optional.of(SystemRole.USER));

        assertThatThrownBy(() -> service.requireReviewer(userId))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> org.assertj.core.api.Assertions.assertThat(((ApiException) error).status().value()).isEqualTo(403));
    }

    @Test
    void reviewerCannotPromoteModels() {
        UUID reviewerId = UUID.randomUUID();
        when(users.systemRole(reviewerId)).thenReturn(Optional.of(SystemRole.REVIEWER));

        assertThatThrownBy(() -> service.requireAdmin(reviewerId))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> org.assertj.core.api.Assertions.assertThat(((ApiException) error).status().value()).isEqualTo(403));
    }
}
