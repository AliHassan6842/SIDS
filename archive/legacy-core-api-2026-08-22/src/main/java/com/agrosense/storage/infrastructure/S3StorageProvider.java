package com.agrosense.storage.infrastructure;

import com.agrosense.storage.domain.StorageProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.core.sync.ResponseTransformer;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

import java.io.InputStream;
import java.util.Optional;

@Service
public class S3StorageProvider implements StorageProvider {

    private final S3Client s3Client;
    private final String bucket;

    public S3StorageProvider(S3Client s3Client, @Value("${agrosense.storage.s3.bucket}") String bucket) {
        this.s3Client = s3Client;
        this.bucket = bucket;
    }

    @Override
    public String store(String objectKey, InputStream content, String contentType, long sizeBytes) {
        PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                .bucket(bucket)
                .key(objectKey)
                .contentType(contentType)
                .build();
        s3Client.putObject(putObjectRequest, RequestBody.fromInputStream(content, sizeBytes));
        return objectKey;
    }

    @Override
    public Optional<InputStream> retrieve(String objectKey) {
        GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                .bucket(bucket)
                .key(objectKey)
                .build();
        try {
            return Optional.of(s3Client.getObject(getObjectRequest, ResponseTransformer.toInputStream()));
        } catch (Exception e) {
            return Optional.empty();
        }
    }

    @Override
    public void delete(String objectKey) {
        DeleteObjectRequest deleteObjectRequest = DeleteObjectRequest.builder()
                .bucket(bucket)
                .key(objectKey)
                .build();
        s3Client.deleteObject(deleteObjectRequest);
    }
}
