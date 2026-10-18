package com.agrosense.storage;

import com.agrosense.shared.error.ApiException;
import java.io.IOException;
import java.nio.file.*;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

@Component
public class PrivateImageStorage {
    private final Path root;
    public PrivateImageStorage(@Value("${sids.storage.local-root}") String root) { this.root = Path.of(root).toAbsolutePath().normalize(); }
    public String save(UUID userId, UUID scanId, byte[] jpeg) {
        String key = userId + "/" + scanId + ".jpg";
        Path target = resolve(key);
        try { Files.createDirectories(target.getParent()); Files.write(target, jpeg, StandardOpenOption.CREATE_NEW); return key; }
        catch (IOException e) { throw new ApiException(HttpStatus.INTERNAL_SERVER_ERROR, "STORAGE_FAILED", "Image could not be stored.", true); }
    }
    public byte[] read(String key) {
        try { return Files.readAllBytes(resolve(key)); }
        catch (IOException e) { throw new ApiException(HttpStatus.NOT_FOUND, "IMAGE_NOT_FOUND", "Scan image was not found.", false); }
    }
    public void delete(String key) {
        try { Files.deleteIfExists(resolve(key)); }
        catch (IOException e) { throw new ApiException(HttpStatus.INTERNAL_SERVER_ERROR, "STORAGE_CLEANUP_FAILED", "Incomplete scan image could not be removed.", true); }
    }
    private Path resolve(String key) {
        Path target = root.resolve(key).normalize();
        if (!target.startsWith(root)) throw new ApiException(HttpStatus.BAD_REQUEST, "INVALID_IMAGE_KEY", "Image key is invalid.", false);
        return target;
    }
}
