package com.agrosense.weather.api;

import com.agrosense.weather.api.request.CreateWeatherSnapshotRequest;
import com.agrosense.weather.application.WeatherService;
import com.agrosense.weather.application.dto.CurrentWeatherDto;
import com.agrosense.weather.application.dto.WeatherAlertDto;
import com.agrosense.weather.application.dto.WeatherForecastDto;
import com.agrosense.weather.application.dto.WeatherSnapshotDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/weather")
@Tag(name = "Weather", description = "Endpoints for current weather observations, forecasts, alerts, and field snapshots")
public class WeatherController {

    private final WeatherService weatherService;

    public WeatherController(WeatherService weatherService) {
        this.weatherService = weatherService;
    }

    @GetMapping("/current")
    @Operation(summary = "Get current weather", description = "Fetches current weather conditions for given coordinates, optionally recording a snapshot for a field.")
    @ApiResponse(responseCode = "200", description = "Current weather retrieved successfully")
    public ResponseEntity<CurrentWeatherDto> getCurrentWeather(
            @Parameter(description = "Latitude in decimal degrees", example = "-17.8252")
            @RequestParam double lat,
            @Parameter(description = "Longitude in decimal degrees", example = "31.0335")
            @RequestParam double lng,
            @Parameter(description = "Optional field ID to associate the observation with")
            @RequestParam(required = false) UUID fieldId,
            @Parameter(description = "Whether to automatically persist a snapshot for the field")
            @RequestParam(defaultValue = "false") boolean snapshot
    ) {
        CurrentWeatherDto response;
        if (fieldId != null) {
            response = weatherService.getCurrentWeatherForField(fieldId, lat, lng, snapshot);
        } else {
            response = weatherService.getCurrentWeather(lat, lng);
        }
        return ResponseEntity.ok(response);
    }

    @GetMapping("/forecast")
    @Operation(summary = "Get daily forecast", description = "Fetches multi-day weather forecast for given coordinates.")
    @ApiResponse(responseCode = "200", description = "Weather forecast retrieved successfully")
    public ResponseEntity<List<WeatherForecastDto>> getForecast(
            @Parameter(description = "Latitude in decimal degrees", example = "-17.8252")
            @RequestParam double lat,
            @Parameter(description = "Longitude in decimal degrees", example = "31.0335")
            @RequestParam double lng,
            @Parameter(description = "Number of days for forecast (1-16)", example = "7")
            @RequestParam(defaultValue = "7") int days
    ) {
        List<WeatherForecastDto> forecasts = weatherService.getForecast(lat, lng, days);
        return ResponseEntity.ok(forecasts);
    }

    @GetMapping("/alerts")
    @Operation(summary = "Get weather alerts", description = "Fetches active severe weather alerts for given coordinates.")
    @ApiResponse(responseCode = "200", description = "Weather alerts retrieved successfully")
    public ResponseEntity<List<WeatherAlertDto>> getAlerts(
            @Parameter(description = "Latitude in decimal degrees", example = "-17.8252")
            @RequestParam double lat,
            @Parameter(description = "Longitude in decimal degrees", example = "31.0335")
            @RequestParam double lng
    ) {
        List<WeatherAlertDto> alerts = weatherService.getAlerts(lat, lng);
        return ResponseEntity.ok(alerts);
    }

    @PostMapping("/snapshots")
    @Operation(summary = "Record weather snapshot", description = "Records a weather snapshot for a field either by providing direct measurements or fetching current provider data.")
    @ApiResponse(responseCode = "201", description = "Weather snapshot created successfully")
    public ResponseEntity<WeatherSnapshotDto> createSnapshot(
            @Valid @RequestBody CreateWeatherSnapshotRequest request
    ) {
        WeatherSnapshotDto saved = weatherService.recordSnapshot(request.toCommand());
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @GetMapping("/snapshots/fields/{fieldId}")
    @Operation(summary = "Get snapshots for field", description = "Retrieves all weather snapshots recorded for a specific field, optionally filtered by timestamp range.")
    @ApiResponse(responseCode = "200", description = "Snapshots retrieved successfully")
    public ResponseEntity<List<WeatherSnapshotDto>> getSnapshotsForField(
            @PathVariable UUID fieldId,
            @Parameter(description = "Start timestamp (ISO-8601 UTC)")
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant from,
            @Parameter(description = "End timestamp (ISO-8601 UTC)")
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant to
    ) {
        List<WeatherSnapshotDto> snapshots = weatherService.getSnapshotHistory(fieldId, from, to);
        return ResponseEntity.ok(snapshots);
    }

    @GetMapping("/snapshots/fields/{fieldId}/latest")
    @Operation(summary = "Get latest snapshot for field", description = "Retrieves the most recent weather snapshot recorded for a specific field.")
    @ApiResponse(responseCode = "200", description = "Latest snapshot retrieved successfully")
    @ApiResponse(responseCode = "404", description = "No snapshot found for field")
    public ResponseEntity<WeatherSnapshotDto> getLatestSnapshotForField(
            @PathVariable UUID fieldId
    ) {
        WeatherSnapshotDto snapshot = weatherService.getLatestSnapshot(fieldId);
        return ResponseEntity.ok(snapshot);
    }

    @GetMapping("/snapshots/{snapshotId}")
    @Operation(summary = "Get snapshot by ID", description = "Retrieves a specific weather snapshot by its ID.")
    @ApiResponse(responseCode = "200", description = "Snapshot retrieved successfully")
    @ApiResponse(responseCode = "404", description = "Snapshot not found")
    public ResponseEntity<WeatherSnapshotDto> getSnapshotById(
            @PathVariable UUID snapshotId
    ) {
        WeatherSnapshotDto snapshot = weatherService.getSnapshotById(snapshotId);
        return ResponseEntity.ok(snapshot);
    }
}
