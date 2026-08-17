package com.agrosense.identity.infrastructure;

import com.agrosense.identity.domain.User;
import org.springframework.data.repository.CrudRepository;
import java.util.Optional;
import java.util.UUID;

public interface UserRepository extends CrudRepository<User, UUID> {
    Optional<User> findBySub(String sub);
}
