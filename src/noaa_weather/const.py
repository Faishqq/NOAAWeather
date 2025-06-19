"""Constants for the NOAA Weather integration."""

from __future__ import annotations

from typing import Final

NOAA_UPDATE_INTERVAL_MIN = 60
API_METRIC: Final = "Metric"
ATTRIBUTION: Final = "Data provided by NOAA"
ATTR_CURRENT_CONDITION: Final = "current_condition"
ATTR_HOURLY_FORECAST: Final = "hourly_forecast"
ATTR_DAILY_FORECAST: Final = "daily_forecast"
DOMAIN = "noaa_weather"
MANUFACTURER: Final = "NOAA NWS"
MAX_FORECAST_DAYS: Final = 14
DEFAULT_HOME_LATITUDE = 37.7690
DEFAULT_HOME_LONGITUDE = -122.4990
CONF_TRACK_HOME = "track_home"
HOME_LOCATION_NAME = "Home"

# Key for the last API update timestamp coming from noaa_client parsers
KEY_LAST_API_UPDATE_FROM_CLIENT = "last_api_update"  # This MUST match the key used in your noaa_client's hourly_forecast.py and daily_forecast.py

# Standard Home Assistant Weather Attributes & Forecast Keys
from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_FORECAST_CLOUD_COVERAGE,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_WEATHER_CLOUD_COVERAGE,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_VISIBILITY,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_GUST_SPEED,
    ATTR_WEATHER_WIND_SPEED,
)

# Attribute name for weather entities
HA_ATTR_LAST_API_UPDATE = "last_api_update"


CONDITIONS_MAP = {
    ATTR_CONDITION_CLEAR_NIGHT: {"clear", "skc"},
    ATTR_CONDITION_CLOUDY: {"cloudy", "ovc", "bkn"},
    ATTR_CONDITION_FOG: {"fog", "mist"},
    ATTR_CONDITION_LIGHTNING_RAINY: {"tsra", "thunderstorm"},
    ATTR_CONDITION_PARTLYCLOUDY: {
        "sct",
        "few",
        "partly cloudy",
        "mostly clear",
        "bkn",
        "partly sunny",
    },
    ATTR_CONDITION_POURING: {"heavy rain", "heavy_rain"},
    ATTR_CONDITION_RAINY: {
        "rain",
        "ra",
        "shra",
        "showers",
        "rain showers",
        "light rain",
    },
    ATTR_CONDITION_SNOWY: {"snow", "sn", "light snow", "heavy snow"},
    ATTR_CONDITION_SNOWY_RAINY: {"rasn", "sleet", "mixed rain and snow", "wintry mix"},
    ATTR_CONDITION_SUNNY: {"clear", "skc", "sunny", "mostly sunny"},
}

ATTR_MAP = {
    ATTR_WEATHER_HUMIDITY: "humidity",
    ATTR_WEATHER_PRESSURE: "native_pressure",
    ATTR_WEATHER_TEMPERATURE: "native_temperature",
    ATTR_WEATHER_WIND_BEARING: "wind_bearing",
    ATTR_WEATHER_WIND_SPEED: "native_wind_speed",
    # Mapping for the weather entity's last_api_update attribute
    HA_ATTR_LAST_API_UPDATE: KEY_LAST_API_UPDATE_FROM_CLIENT,
}

FORECAST_MAP = {
    ATTR_FORECAST_CONDITION: "condition",
    ATTR_FORECAST_NATIVE_PRECIPITATION: "native_precipitation",
    ATTR_FORECAST_PRECIPITATION_PROBABILITY: "precipitation_probability",
    ATTR_FORECAST_NATIVE_TEMP: "native_temperature",
    ATTR_FORECAST_NATIVE_TEMP_LOW: "native_templow",
    ATTR_FORECAST_TIME: "datetime",
    ATTR_FORECAST_WIND_BEARING: "wind_bearing",
    ATTR_FORECAST_NATIVE_WIND_SPEED: "native_wind_speed",
    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED: "native_wind_gust_speed",
    ATTR_FORECAST_CLOUD_COVERAGE: "cloud_coverage",
    ATTR_FORECAST_HUMIDITY: "humidity",
    ATTR_WEATHER_PRESSURE: "native_pressure",
    # Mapping for the weather entity's last_api_update attribute (when sourced from daily forecast)
    # and for the forecast list items if we wanted to include it there (not typical for HA Forecast TypedDict)
    HA_ATTR_LAST_API_UPDATE: KEY_LAST_API_UPDATE_FROM_CLIENT,
}
