package com.agrosense.weather.domain;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class WeatherConditionTest {

    @Test
    @DisplayName("Should correctly map WMO codes to WeatherCondition enum values")
    void testFromWmoCode() {
        assertThat(WeatherCondition.fromWmoCode(0)).isEqualTo(WeatherCondition.CLEAR);
        assertThat(WeatherCondition.fromWmoCode(1)).isEqualTo(WeatherCondition.MAINLY_CLEAR);
        assertThat(WeatherCondition.fromWmoCode(2)).isEqualTo(WeatherCondition.PARTLY_CLOUDY);
        assertThat(WeatherCondition.fromWmoCode(3)).isEqualTo(WeatherCondition.OVERCAST);
        assertThat(WeatherCondition.fromWmoCode(45)).isEqualTo(WeatherCondition.FOG);
        assertThat(WeatherCondition.fromWmoCode(51)).isEqualTo(WeatherCondition.DRIZZLE);
        assertThat(WeatherCondition.fromWmoCode(61)).isEqualTo(WeatherCondition.RAIN);
        assertThat(WeatherCondition.fromWmoCode(65)).isEqualTo(WeatherCondition.HEAVY_RAIN);
        assertThat(WeatherCondition.fromWmoCode(71)).isEqualTo(WeatherCondition.SNOW);
        assertThat(WeatherCondition.fromWmoCode(95)).isEqualTo(WeatherCondition.THUNDERSTORM);
        assertThat(WeatherCondition.fromWmoCode(999)).isEqualTo(WeatherCondition.UNKNOWN);
    }
}
