package com.agrosense.identity.infrastructure;

import com.agrosense.identity.domain.UserProfile;
import com.agrosense.identity.domain.SystemRole;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class UserRepository {
    private final JdbcTemplate jdbc;
    public UserRepository(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    public Optional<UserProfile> findByEmail(String email) {
        List<UserProfile> rows = jdbc.query("SELECT id,email,name,language,password_hash FROM users WHERE LOWER(email)=LOWER(?)", this::map, email);
        return rows.stream().findFirst();
    }
    public Optional<UserProfile> findById(UUID id) {
        List<UserProfile> rows = jdbc.query("SELECT id,email,name,language,password_hash FROM users WHERE id=?", this::map, id);
        return rows.stream().findFirst();
    }
    public Optional<SystemRole> systemRole(UUID id) {
        return jdbc.query("SELECT system_role FROM users WHERE id=?",
            (rs, row) -> SystemRole.valueOf(rs.getString(1)), id).stream().findFirst();
    }
    public UserProfile create(String email, String fullName, String language, String passwordHash) {
        UUID id = UUID.randomUUID();
        OffsetDateTime now = OffsetDateTime.now();
        jdbc.update("INSERT INTO users(id,sub,email,name,password_hash,language,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",
            id, "local:" + id, email.toLowerCase(), fullName, passwordHash, language, now, now);
        return new UserProfile(id, email.toLowerCase(), fullName, language, passwordHash);
    }
    public void update(UUID id, String fullName, String language) {
        jdbc.update("UPDATE users SET name=?,language=COALESCE(?,language),updated_at=? WHERE id=?", fullName, language, OffsetDateTime.now(), id);
    }
    private UserProfile map(ResultSet rs, int row) throws SQLException {
        return new UserProfile(rs.getObject("id", UUID.class), rs.getString("email"), rs.getString("name"),
            rs.getString("language"), rs.getString("password_hash"));
    }
}
