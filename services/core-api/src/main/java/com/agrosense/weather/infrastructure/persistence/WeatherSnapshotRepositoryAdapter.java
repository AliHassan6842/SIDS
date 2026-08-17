package com.agrosense.weather.infrastructure.persistence;

import com.agrosense.weather.domain.WeatherSnapshot;
import com.agrosense.weather.domain.WeatherSnapshotRepository;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public class WeatherSnapshotRepositoryAdapter implements WeatherSnapshotRepository {

    private final SpringDataWeatherSnapshotRepository springDataRepository;

    public WeatherSnapshotRepositoryAdapter(SpringDataWeatherSnapshotRepository springDataRepository) {
        this.springDataRepository = springDataRepository;
    }

    @Override
    public WeatherSnapshot save(WeatherSnapshot snapshot) {
        WeatherSnapshotEntity entity = WeatherSnapshotEntity.fromDomain(snapshot);
        WeatherSnapshotEntity saved = springDataRepository.save(entity);
        return saved.toDomain();
    }

    @Override
    public Optional<WeatherSnapshot> findById(UUID id) {
        return springDataRepository.findById(id)
                .map(WeatherSnapshotEntity::toDomain);
    }

    @Override
    public List<WeatherSnapshot> findByFieldId(UUID fieldId) {
        return springDataRepository.findByFieldIdOrderByTimestampDesc(fieldId)
                .stream()
                .map(WeatherSnapshotEntity::toDomain)
                .toList();
    }

    @Override
    public Optional<WeatherSnapshot> findLatestByFieldId(UUID fieldId) {
        return springDataRepository.findFirstByFieldIdOrderByTimestampDesc(fieldId)
                .map(WeatherSnapshotEntity::toDomain);
    }

    @Override
    public List<WeatherSnapshot> findByFieldIdAndTimestampBetween(UUID fieldId, Instant start, Instant end) {
        return springDataRepository.findByFieldIdAndTimestampBetweenOrderByTimestampDesc(fieldId, start, end)
                .stream()
                .map(WeatherSnapshotEntity::toDomain)
                .toList();
    }

    @Override
    public void deleteById(UUID id) {
        springDataRepository.deleteById(id);
    }
}
