"""Support for NOAA weather service."""

from __future__ import annotations
from datetime import datetime  # For type hinting
import logging

from typing import Any

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_WEATHER_CLOUD_COVERAGE,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_GUST_SPEED,
    ATTR_WEATHER_WIND_SPEED,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_CLOUD_COVERAGE,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_WIND_BEARING,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify, dt as dt_util

from . import NOAAWeatherDataUpdateCoordinator
from . import const  # Import the main const module
from .const import DOMAIN, HA_ATTR_LAST_API_UPDATE  # Import specific constants

DEFAULT_NAME = "NOAA Weather"
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add weather entities from a config_entry."""
    coordinator: NOAAWeatherDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities_to_add = [
        NOAAWeather(
            coordinator=coordinator,
            is_metric=True,  # Assuming metric
            hourly=True,
        ),
        NOAAWeather(
            coordinator=coordinator,
            is_metric=True,  # Assuming metric
            hourly=False,  # For the daily weather entity
        ),
    ]

    async_add_entities(entities_to_add)


class NOAAWeather(CoordinatorEntity[NOAAWeatherDataUpdateCoordinator], WeatherEntity):
    """Implementation of NOAA weather condition."""

    _attr_attribution = "Data provided by NOAA"
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND

    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY
    )

    def __init__(
        self,
        coordinator: NOAAWeatherDataUpdateCoordinator,
        is_metric: bool,
        hourly: bool,
    ) -> None:
        """Initialise the platform."""
        super().__init__(coordinator)
        self._hourly = hourly
        self._base_entity_name = coordinator.location_name or DEFAULT_NAME
        location_name_slug = slugify(self._base_entity_name)
        type_slug = "hourly" if self._hourly else "daily"
        self._attr_unique_id = f"{location_name_slug}_{type_slug}_weather"


    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added."""
        return True

    @property
    def name(self) -> str:
        """Return the friendly name of the entity."""
        type_suffix = " Hourly" if self._hourly else " Daily"
        return f"{self._base_entity_name}{type_suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information to link to coordinator's device."""
        return self.coordinator.device_info

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        # Get the last_api_update timestamp from the first forecast item
        # This timestamp comes from your noaa_client's _forecast_at
        last_update_from_forecast_data_float = self._get_current_or_first_daily_value(
            HA_ATTR_LAST_API_UPDATE
        )

        if last_update_from_forecast_data_float is not None:
            try:
                # Convert float timestamp to datetime object, then to ISO string
                dt_object = dt_util.utc_from_timestamp(
                    float(last_update_from_forecast_data_float)
                )
                attrs[HA_ATTR_LAST_API_UPDATE] = dt_object.isoformat()
            except (ValueError, TypeError) as e:
                _LOGGER.warning(
                    "WEATHER PLATFORM (%s): Could not convert %s value '%s' to datetime: %s",
                    self.name,
                    HA_ATTR_LAST_API_UPDATE,
                    last_update_from_forecast_data_float,
                    e,
                )

        # Also include the coordinator's last successful data fetch time for broader context
        if (
            hasattr(self.coordinator, "last_update_success_time")
            and self.coordinator.last_update_success_time
        ):
            attrs["coordinator_last_fetch"] = (
                self.coordinator.last_update_success_time.isoformat()
            )

        return attrs

    def _get_current_or_first_daily_value(
        self, ha_weather_attr_const: str, source_data_key_override: str | None = None
    ):
        """Helper to get value from current conditions or first daily forecast item."""
        if self.coordinator.data is None:
            _LOGGER.warning(
                "WEATHER PLATFORM (%s): Coordinator data is None in helper.", self.name
            )
            return None

        source_data_dict: dict | None = None
        key_in_source_data: str | None = None

        if self._hourly:
            source_data_dict = self.coordinator.data.get(const.ATTR_CURRENT_CONDITION)
            key_in_source_data = (
                source_data_key_override
                if source_data_key_override
                else const.ATTR_MAP.get(ha_weather_attr_const)
            )
        else:
            daily_forecast_list = self.coordinator.data.get(const.ATTR_DAILY_FORECAST)
            if (
                not daily_forecast_list
                or not isinstance(daily_forecast_list, list)
                or len(daily_forecast_list) == 0
            ):
                _LOGGER.warning( 
                    "WEATHER PLATFORM (%s): Daily forecast list is empty or not found.",
                    self.name,
                )
                return None
            source_data_dict = daily_forecast_list[0]
            key_in_source_data = (
                source_data_key_override
                if source_data_key_override
                else const.FORECAST_MAP.get(ha_weather_attr_const)
            )

        if source_data_dict is None:
            _LOGGER.warning(
                "WEATHER PLATFORM (%s): Source data dict is None for HA attr %s.",
                self.name,
                ha_weather_attr_const,
            )
            return None
        if key_in_source_data is None:
            _LOGGER.warning(
                "WEATHER PLATFORM (%s): No mapping found for HA attr %s in relevant map.",
                self.name,
                ha_weather_attr_const,
            )
            return None

        value = source_data_dict.get(key_in_source_data)
        if value is None:
            _LOGGER.warning(
                "WEATHER PLATFORM (%s): Key '%s' not found in source data for HA attr %s.",
                self.name,
                key_in_source_data,
                ha_weather_attr_const,
            )
            return None

        # For HA_ATTR_LAST_API_UPDATE, the value is already a float timestamp from noaa_client
        if ha_weather_attr_const == HA_ATTR_LAST_API_UPDATE:
            try:
                return float(value)
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "WEATHER PLATFORM (%s): %s value '%s' is not a valid float.",
                    self.name,
                    HA_ATTR_LAST_API_UPDATE,
                    value,
                )
                return None

        numeric_attrs = [
            ATTR_WEATHER_TEMPERATURE,
            ATTR_WEATHER_PRESSURE,
            ATTR_WEATHER_HUMIDITY,
            ATTR_WEATHER_WIND_SPEED,
            ATTR_WEATHER_WIND_GUST_SPEED,
            ATTR_WEATHER_CLOUD_COVERAGE,
            ATTR_FORECAST_NATIVE_TEMP,
            ATTR_FORECAST_NATIVE_TEMP_LOW,
        ]
        if ha_weather_attr_const in numeric_attrs:
            try:
                return float(value)
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "WEATHER PLATFORM (%s): Could not convert value '%s' (from key '%s') to float for HA attr %s.",
                    self.name,
                    value,
                    key_in_source_data,
                    ha_weather_attr_const,
                )
                return None
        return value

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        raw_condition = self._get_current_or_first_daily_value(
            ATTR_FORECAST_CONDITION,
            "condition",  # "condition" is the direct key in your data
        )
        if raw_condition is None:
            return None
        for ha_cond, noaa_conds in const.CONDITIONS_MAP.items():
            if isinstance(raw_condition, str) and raw_condition.lower() in noaa_conds:
                return ha_cond
        _LOGGER.warning(
            "WEATHER PLATFORM (%s): Unmapped condition: %s", self.name, raw_condition
        )
        return raw_condition if isinstance(raw_condition, str) else None

    @property
    def native_temperature(self) -> float | None:
        if self._hourly:
            return self._get_current_or_first_daily_value(ATTR_WEATHER_TEMPERATURE)
        return self._get_current_or_first_daily_value(ATTR_FORECAST_NATIVE_TEMP)

    @property
    def native_temperature_low(self) -> float | None:
        if not self._hourly:
            return self._get_current_or_first_daily_value(ATTR_FORECAST_NATIVE_TEMP_LOW)
        return None

    @property
    def native_pressure(self) -> float | None:
        return self._get_current_or_first_daily_value(ATTR_WEATHER_PRESSURE)

    @property
    def humidity(self) -> float | None:
        return self._get_current_or_first_daily_value(ATTR_WEATHER_HUMIDITY)

    @property
    def native_wind_speed(self) -> float | None:
        return self._get_current_or_first_daily_value(ATTR_WEATHER_WIND_SPEED)

    @property
    def wind_bearing(self) -> float | str | None:
        return self._get_current_or_first_daily_value(ATTR_WEATHER_WIND_BEARING)

    def _prepare_forecast(
        self, forecast_data: list[dict[str, Any]] | None
    ) -> list[Forecast] | None:
        if not forecast_data or not isinstance(forecast_data, list):
            _LOGGER.warning(
                "WEATHER PLATFORM (%s): No forecast data or invalid format for processing.",
                self.name,
            )
            return None

        ha_forecast: list[Forecast] = []
        for item in forecast_data:
            if not isinstance(item, dict):
                _LOGGER.warning(
                    "WEATHER PLATFORM (%s): Forecast item is not a dict: %s",
                    self.name,
                    item,
                )
                continue

            mapped_item: Forecast = {}
            for ha_key, api_key in const.FORECAST_MAP.items():
                # Do not include the HA_ATTR_LAST_API_UPDATE in individual forecast list items
                if ha_key == HA_ATTR_LAST_API_UPDATE:
                    continue

                if item.get(api_key) is not None:
                    if ha_key == ATTR_FORECAST_CONDITION:
                        raw_condition = item.get(api_key)
                        mapped_condition = raw_condition
                        if isinstance(raw_condition, str):
                            for (
                                ha_cond_const,
                                noaa_conds,
                            ) in const.CONDITIONS_MAP.items():
                                if raw_condition.lower() in noaa_conds:
                                    mapped_condition = ha_cond_const
                                    break
                        mapped_item[ha_key] = mapped_condition
                    else:
                        mapped_item[ha_key] = item.get(api_key)

            if ATTR_FORECAST_TIME not in mapped_item:
                _LOGGER.warning(
                    "WEATHER PLATFORM (%s): Forecast item skipped, missing mapped datetime for original item: %s",
                    self.name,
                    item,
                )
                continue

            numeric_ha_forecast_keys = [
                ATTR_FORECAST_NATIVE_TEMP,
                ATTR_FORECAST_NATIVE_TEMP_LOW,
                ATTR_FORECAST_NATIVE_PRECIPITATION,
                ATTR_FORECAST_PRECIPITATION_PROBABILITY,
                ATTR_FORECAST_NATIVE_WIND_SPEED,
                ATTR_FORECAST_NATIVE_WIND_GUST_SPEED,
                ATTR_FORECAST_CLOUD_COVERAGE,
                ATTR_FORECAST_HUMIDITY,
            ]

            for key_to_check in numeric_ha_forecast_keys:
                if mapped_item.get(key_to_check) is not None:
                    current_val = mapped_item.get(key_to_check)
                    if not isinstance(current_val, (float, int)):
                        try:
                            mapped_item[key_to_check] = float(current_val)
                        except (ValueError, TypeError):
                            _LOGGER.warning(
                                "WEATHER PLATFORM (%s): Could not convert forecast value for '%s' to float: %s. Removing.",
                                self.name,
                                key_to_check,
                                current_val,
                            )
                            del mapped_item[key_to_check]

            if mapped_item:
                ha_forecast.append(mapped_item)

        _LOGGER.info(
            "WEATHER PLATFORM (%s): Prepared HA forecast with %d items.",
            self.name,
            len(ha_forecast),
        )
        return ha_forecast

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        if not self._hourly:
            return None
        if self.coordinator.data:
            raw_hourly_forecast = self.coordinator.data.get(const.ATTR_HOURLY_FORECAST)
            return self._prepare_forecast(raw_hourly_forecast)
        return None

    async def async_forecast_daily(self) -> list[Forecast] | None:
        if self._hourly:
            return None
        if self.coordinator.data:
            raw_daily_forecast = self.coordinator.data.get(const.ATTR_DAILY_FORECAST)
            return self._prepare_forecast(raw_daily_forecast)
        _LOGGER.warning(
            "WEATHER PLATFORM (%s): No coordinator data for daily forecast.", self.name
        )
        return None
