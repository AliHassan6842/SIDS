package com.agrosense.weather.domain;

public enum WeatherCondition {
    CLEAR("Clear sky"),
    MAINLY_CLEAR("Mainly clear"),
    PARTLY_CLOUDY("Partly cloudy"),
    OVERCAST("Overcast"),
    FOG("Foggy"),
    DRIZZLE("Drizzle"),
    RAIN("Rain"),
    HEAVY_RAIN("Heavy rain"),
    THUNDERSTORM("Thunderstorm"),
    SNOW("Snow"),
    HAIL("Hail"),
    UNKNOWN("Unknown");

    private final String description;

    WeatherCondition(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    public static WeatherCondition fromWmoCode(int code) {
        return switch (code) {
            case 0 -> CLEAR;
            case 1 -> MAINLY_CLEAR;
            case 2 -> PARTLY_CLOUDY;
            case 3 -> OVERCAST;
            case 45, 48 -> FOG;
            case 51, 53, 55 -> DRIZZLE;
            case 61, 63 -> RAIN;
            case 65, 80, 81, 82 -> HEAVY_RAIN;
            case 71, 73, 75, 77, 85, 86 -> SNOW;
            case 95, 96, 99 -> THUNDERSTORM;
            default -> UNKNOWN;
        };
    }
}
