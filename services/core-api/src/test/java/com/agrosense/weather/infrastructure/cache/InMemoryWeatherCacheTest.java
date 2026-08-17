package com.agrosense.weather.infrastructure.cache;

import com.agrosense.weather.domain.WeatherCondition;
import com.agrosense.weather.domain.WeatherData;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

class InMemoryWeatherCacheTest {

    private InMemoryWeatherCache cache;

    @BeforeEach
    void setUp() {
        cache = new InMemoryWeatherCache();
    }

    @Test
    @DisplayName("Should store and retrieve weather data for matching coordinates")
    void testPutAndGet() {
        double lat = -17.8252;
        double lng = 31.0335;
        WeatherData data = WeatherData.builder()
                .temperature(25.0)
                .humidity(60.0)
                .condition(WeatherCondition.CLEAR)
                .build();

        cache.put(lat, lng, data, 60);

        Optional<WeatherData> retrieved = cache.get(lat, lng);
        assertThat(retrieved).isPresent();
        assertThat(retrieved.get().temperature()).isEqualTo(25.0);
    }

    @Test
    @DisplayName("Should match nearby coordinates within rounding threshold")
    void testCoordinateRounding() {
        double lat1 = -17.82521;
        double lng1 = 31.03351;
        double lat2 = -17.82524;
        double lng2 = 31.03354;

        WeatherData data = WeatherData.builder()
                .temperature(22.0)
                .condition(WeatherCondition.PARTLY_CLOUDY)
                .build();

        cache.put(lat1, lng1, data, 60);

        Optional<WeatherData> retrieved = cache.get(lat2, lng2);
        assertThat(retrieved).isPresent();
        assertThat(retrieved.get().temperature()).isEqualTo(22.0);
    }

    @Test
    @DisplayName("Should return empty for expired entries")
    void testExpiredEntry() throws InterruptedException {
        double lat = 10.0;
        double lng = 20.0;
        WeatherData data = WeatherData.builder().temperature(30.0).build();

        // Expire immediately with 0 second TTL
        cache.put(lat, lng, data, 0);
        Thread.sleep(10);

        Optional<WeatherData> retrieved = cache.get(lat, lng);
        assertThat(retrieved).isEmpty();
    }

    @Test
    @DisplayName("Should evict entry on demand")
    void testEvict() {
        double lat = 12.34;
        double lng = 56.78;
        WeatherData data = WeatherData.builder().temperature(20.0).build();

        cache.put(lat, lng, data, 60);
        assertThat(cache.get(lat, lng)).isPresent();

        cache.evict(lat, lng);
        assertThat(cache.get(lat, lng)).isEmpty();
    }
}
