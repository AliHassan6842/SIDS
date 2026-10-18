package com.agrosense.sync.domain;

import com.agrosense.sync.domain.model.OptimisticLockVersion;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class OptimisticLockVersionTest {

    @Test
    void shouldDetectNoConflictWhenVersionsMatch() {
        OptimisticLockVersion lockVersion = new OptimisticLockVersion(3L, 3L);

        assertFalse(lockVersion.hasConflict());
        assertFalse(lockVersion.isStale());
        assertEquals(4L, lockVersion.nextVersion());
    }

    @Test
    void shouldDetectConflictWhenBaseVersionIsStale() {
        OptimisticLockVersion lockVersion = new OptimisticLockVersion(2L, 5L);

        assertTrue(lockVersion.hasConflict());
        assertTrue(lockVersion.isStale());
        assertEquals(6L, lockVersion.nextVersion());
    }

    @Test
    void shouldDetectConflictWhenBaseVersionIsAhead() {
        OptimisticLockVersion lockVersion = new OptimisticLockVersion(5L, 2L);

        assertTrue(lockVersion.hasConflict());
        assertFalse(lockVersion.isStale());
    }

    @Test
    void shouldHandleNullVersionsSafely() {
        OptimisticLockVersion lockVersion1 = new OptimisticLockVersion(null, 1L);
        assertFalse(lockVersion1.hasConflict());

        OptimisticLockVersion lockVersion2 = new OptimisticLockVersion(1L, null);
        assertFalse(lockVersion2.hasConflict());
        assertEquals(1L, lockVersion2.nextVersion());
    }
}
