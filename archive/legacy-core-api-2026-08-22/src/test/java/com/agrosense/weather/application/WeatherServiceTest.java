package com.agrosense.weather.application;

import com.agrosense.shared.error.exceptions.ResourceNotFoundException;
import com.agrosense.weather.application.dto.CurrentWeatherDto;
import com.agrosense.weather.application.dto.RecordSnapshotCommand;
import com.agrosense.weather.application.dto.WeatherSnapshotDto;
import com.agrosense.weather.domain.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WeatherServiceTest {

    @Mock
    private WeatherProvider weatherProvider;

    @Mock
    private WeatherSnapshotRepository snapshotRepository;

    @Mock
    private WeatherCache weatherCache;

    private WeatherService weatherService;

    @BeforeEach
    void setUp() {
        weatherService = new WeatherService(weatherProvider, snapshotRepository, weatherCache);
    }

    @Test
    @DisplayName("Should return cached weather data when available")
    void testGetCurrentWeather_CacheHit() {
        double lat = -17.8252;
        double lng = 31.0335;
        WeatherData cachedData = WeatherData.builder()
                .temperature(25.0)
                .humidity(60.0)
                .precipitation(0.0)
                .windSpeed(5.0)
                .condition(WeatherCondition.CLEAR)
                .provider("test-provider")
                .build();

        when(weatherCache.get(lat, lng)).thenReturn(Optional.of(cachedData));

        CurrentWeatherDto result = weatherService.getCurrentWeather(lat, lng);

        assertThat(result).isNotNull();
        assertThat(result.temperature()).isEqualTo(25.0);
        assertThat(result.humidity()).isEqualTo(60.0);
        assertThat(result.condition()).isEqualTo("CLEAR");

        verify(weatherProvider, never()).getCurrentWeather(anyDouble(), anyDouble());
    }

    @Test
    @DisplayName("Should fetch from provider and cache when cache misses")
    void testGetCurrentWeather_CacheMiss() {
        double lat = -17.8252;
        double lng = 31.0335;
        WeatherData freshData = WeatherData.builder()
                .temperature(28.5)
                .humidity(45.0)
                .precipitation(1.2)
                .windSpeed(8.0)
                .condition(WeatherCondition.RAIN)
                .provider("open-meteo")
                .build();

        when(weatherCache.get(lat, lng)).thenReturn(Optional.empty());
        when(weatherProvider.getCurrentWeather(lat, lng)).thenReturn(freshData);

        CurrentWeatherDto result = weatherService.getCurrentWeather(lat, lng);

        assertThat(result).isNotNull();
        assertThat(result.temperature()).isEqualTo(28.5);
        assertThat(result.condition()).isEqualTo("RAIN");

        verify(weatherCache).put(eq(lat), eq(lng), eq(freshData), anyLong());
    }

    @Test
    @DisplayName("Should record snapshot from provider data for a field")
    void testRecordSnapshot_FromProvider() {
        UUID fieldId = UUID.randomUUID();
        double lat = -17.8252;
        double lng = 31.0335;
        WeatherData weatherData = WeatherData.builder()
                .temperature(22.0)
                .humidity(70.0)
                .precipitation(0.0)
                .windSpeed(4.0)
                .provider("simulated")
                .build();

        when(weatherProvider.getCurrentWeather(lat, lng)).thenReturn(weatherData);
        when(snapshotRepository.save(any(WeatherSnapshot.class))).thenAnswer(inv -> inv.getArgument(0));

        WeatherSnapshotDto snapshot = weatherService.recordSnapshot(fieldId, lat, lng);

        assertThat(snapshot).isNotNull();
        assertThat(snapshot.fieldId()).isEqualTo(fieldId);
        assertThat(snapshot.temperature()).isEqualTo(22.0);
        assertThat(snapshot.humidity()).isEqualTo(70.0);

        verify(snapshotRepository).save(any(WeatherSnapshot.class));
    }

    @Test
    @DisplayName("Should record snapshot with direct measurements")
    void testRecordSnapshot_DirectMeasurements() {
        UUID fieldId = UUID.randomUUID();
        RecordSnapshotCommand cmd = new RecordSnapshotCommand(
                fieldId,
                null,
                null,
                26.4,
                55.0,
                0.0,
                3.2,
                "iot-station",
                "{\"stationId\":\"ST-100\"}",
                Instant.now()
        );

        when(snapshotRepository.save(any(WeatherSnapshot.class))).thenAnswer(inv -> inv.getArgument(0));

        WeatherSnapshotDto snapshot = weatherService.recordSnapshot(cmd);

        assertThat(snapshot).isNotNull();
        assertThat(snapshot.fieldId()).isEqualTo(fieldId);
        assertThat(snapshot.temperature()).isEqualTo(26.4);
        assertThat(snapshot.humidity()).isEqualTo(55.0);
        assertThat(snapshot.provider()).isEqualTo("iot-station");

        verify(weatherProvider, never()).getCurrentWeather(anyDouble(), anyDouble());
        verify(snapshotRepository).save(any(WeatherSnapshot.class));
    }

    @Test
    @DisplayName("Should retrieve latest snapshot for field")
    void testGetLatestSnapshot_Success() {
        UUID fieldId = UUID.randomUUID();
        WeatherSnapshot snapshot = new WeatherSnapshot(
                UUID.randomUUID(),
                fieldId,
                24.0,
                65.0,
                0.0,
                5.0,
                "test",
                null,
                Instant.now()
        );

        when(snapshotRepository.findLatestByFieldId(fieldId)).thenReturn(Optional.of(snapshot));

        WeatherSnapshotDto result = weatherService.getLatestSnapshot(fieldId);

        assertThat(result).isNotNull();
        assertThat(result.fieldId()).isEqualTo(fieldId);
        assertThat(result.temperature()).isEqualTo(24.0);
    }

    @Test
    @DisplayName("Should throw ResourceNotFoundException when no latest snapshot exists")
    void testGetLatestSnapshot_NotFound() {
        UUID fieldId = UUID.randomUUID();
        when(snapshotRepository.findLatestByFieldId(fieldId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> weatherService.getLatestSnapshot(fieldId))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining(fieldId.toString());
    }

    @Test
    @DisplayName("Should return snapshot history for field")
    void testGetSnapshotHistory() {
        UUID fieldId = UUID.randomUUID();
        WeatherSnapshot s1 = new WeatherSnapshot(UUID.randomUUID(), fieldId, 24.0, 60.0, 0.0, 3.0, "test", null, Instant.now());
        WeatherSnapshot s2 = new WeatherSnapshot(UUID.randomUUID(), fieldId, 25.0, 58.0, 0.0, 4.0, "test", null, Instant.now().minusSeconds(3600));

        when(snapshotRepository.findByFieldId(fieldId)).thenReturn(List.of(s1, s2));

        List<WeatherSnapshotDto> history = weatherService.getSnapshotHistory(fieldId, null, null);

        assertThat(history).hasSize(2);
        assertThat(history.get(0).temperature()).isEqualTo(24.0);
        assertThat(history.get(1).temperature()).isEqualTo(25.0);
    }
}
