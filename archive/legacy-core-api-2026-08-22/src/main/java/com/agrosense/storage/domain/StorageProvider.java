package com.agrosense.storage.domain;

import java.io.InputStream;
import java.util.Optional;

public interface StorageProvider {
    String store(String objectKey, InputStream content, String contentType, long sizeBytes);
    Optional<InputStream> retrieve(String objectKey);
    void delete(String objectKey);
}
