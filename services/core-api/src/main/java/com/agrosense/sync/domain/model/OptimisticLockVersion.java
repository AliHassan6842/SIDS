package com.agrosense.sync.domain.model;

import java.util.Objects;

/**
 * Value object representing optimistic lock version evaluation between client and server.
 */
public class OptimisticLockVersion {

    private final Long clientBaseVersion;
    private final Long serverCurrentVersion;

    public OptimisticLockVersion(Long clientBaseVersion, Long serverCurrentVersion) {
        this.clientBaseVersion = clientBaseVersion;
        this.serverCurrentVersion = serverCurrentVersion;
    }

    public Long getClientBaseVersion() {
        return clientBaseVersion;
    }

    public Long getServerCurrentVersion() {
        return serverCurrentVersion;
    }

    /**
     * Checks if a conflict exists between the client base version and current server version.
     * A conflict occurs if server version exists, base version exists, and they differ.
     */
    public boolean hasConflict() {
        if (serverCurrentVersion == null || clientBaseVersion == null) {
            return false;
        }
        return !Objects.equals(clientBaseVersion, serverCurrentVersion);
    }

    /**
     * Checks if the client's version is strictly behind the current server version (stale update).
     */
    public boolean isStale() {
        if (serverCurrentVersion == null || clientBaseVersion == null) {
            return false;
        }
        return serverCurrentVersion > clientBaseVersion;
    }

    /**
     * Computes the next expected version after a successful mutation.
     */
    public Long nextVersion() {
        if (serverCurrentVersion == null) {
            return 1L;
        }
        return serverCurrentVersion + 1L;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        OptimisticLockVersion that = (OptimisticLockVersion) o;
        return Objects.equals(clientBaseVersion, that.clientBaseVersion) &&
                Objects.equals(serverCurrentVersion, that.serverCurrentVersion);
    }

    @Override
    public int hashCode() {
        return Objects.hash(clientBaseVersion, serverCurrentVersion);
    }

    @Override
    public String toString() {
        return "OptimisticLockVersion{" +
                "clientBaseVersion=" + clientBaseVersion +
                ", serverCurrentVersion=" + serverCurrentVersion +
                ", hasConflict=" + hasConflict() +
                '}';
    }
}
