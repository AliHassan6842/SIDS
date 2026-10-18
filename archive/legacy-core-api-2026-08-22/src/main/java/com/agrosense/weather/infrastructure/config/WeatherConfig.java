package com.agrosense.weather.infrastructure.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;

@Configuration
@EnableConfigurationProperties(WeatherProperties.class)
@EnableScheduling
public class WeatherConfig {
}
