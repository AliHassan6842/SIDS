package com.agrosense.weather.infrastructure.cache;

import com.agrosense.weather.domain.WeatherCache;
import com.agrosense.weather.domain.WeatherData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Locale;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class InMemoryWeatherCache implements WeatherCache {

    private static final Logger log = LoggerFactory.getLogger(InMemoryWeatherCache.class);

    private final ConcurrentHashMap<String, CacheEntry> cache = new ConcurrentHashMap<>();

    private record CacheEntry(WeatherData data, Instant expiresAt) {
        boolean isExpired() {
            return Instant.now().isAfter(expiresAt);
        }
    }

    @Override
    public Optional<WeatherData> get(double latitude, double longitude) {
        String key = generateKey(latitude, longitude);
        CacheEntry entry = cache.get(key);
        if (entry == null) {
            return Optional.empty();
        }
        if (entry.isExpired()) {
            cache.remove(key);
            return Optional.empty();
        }
        return Optional.of(entry.data());
    }

    @Override
    public void put(double latitude, double longitude, WeatherData data, long ttlSeconds) {
        String key = generateKey(latitude, longitude);
        Instant expiresAt = Instant.now().plusSeconds(ttlSeconds);
        cache.put(key, new CacheEntry(data, expiresAt));
        log.trace("Cached weather data for key {} expiring at {}", key, expiresAt);
    }

    @Override
    public void evict(double latitude, double longitude) {
        String key = generateKey(latitude, longitude);
        cache.remove(key);
    }

    @Override
    public void clear() {
        cache.clear();
    }

    /**
     * Purge expired entries periodically (every 10 minutes).
     */
    @Scheduled(fixedRate = 600000)
    public void cleanupExpiredEntries() {
        int initialSize = cache.size();
        cache.entrySet().removeIf(entry -> entry.getValue().isExpired());
        int removed = initialSize - cache.size();
        if (removed > 0) {
            log.debug("Cleaned up {} expired weather cache entries", removed);
        }
    }

    /**
     * Quantize coordinates to ~3 decimal places (~100m grid) to maximize cache hits for adjacent points.
     */
    private String generateKey(double latitude, double longitude) {
        return String.format(Locale.ROOT, "%.3f:%.3f", latitude, longitude);
    }
}
