"""Support for the NOAAWeather service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any, cast, List

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify, dt as dt_util

from . import NOAAWeatherDataUpdateCoordinator
from . import const  # Import the main const module
from .const import (
    ATTR_DAILY_FORECAST,
    ATTR_HOURLY_FORECAST,
    DOMAIN,
    KEY_LAST_API_UPDATE_FROM_CLIENT,  # Import the key for data from noaa_client
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class NOAAWeatherSensorDescriptionMixin:
    """Mixin for NOAA Weather sensor."""

    value_fn: Callable[[Any], StateType]


@dataclass
class NOAAWeatherSensorDescription(
    SensorEntityDescription, NOAAWeatherSensorDescriptionMixin
):
    """Class describing NOAAWeather sensor entities."""


FORECAST_SENSOR_TYPES: tuple[NOAAWeatherSensorDescription, ...] = (
    NOAAWeatherSensorDescription(
        key="condition",
        name="Weather",
        icon="mdi:weather-partly-cloudy",
        value_fn=lambda data: cast(str, data) if data is not None else None,
    ),
    NOAAWeatherSensorDescription(
        key="humidity",
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data)
        if data is not None and isinstance(data, (float, int))
        else (
            int(float(data))
            if data is not None and str(data).replace(".", "", 1).isdigit()
            else None
        ),
    ),
    NOAAWeatherSensorDescription(
        key="precipitation_probability",
        name="Precipitation Probability",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:weather-rainy",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data)
        if data is not None and isinstance(data, (float, int))
        else (
            int(float(data))
            if data is not None and str(data).replace(".", "", 1).isdigit()
            else None
        ),
    ),
    NOAAWeatherSensorDescription(
        key="native_pressure",
        name="Pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(float(data), 2)
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    NOAAWeatherSensorDescription(
        key="native_temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(float(data), 1)
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    NOAAWeatherSensorDescription(
        key="native_templow",
        name="Low Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(float(data), 1)
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    NOAAWeatherSensorDescription(
        key="native_apparent_temperature",
        name="Apparent Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(float(data), 1)
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    NOAAWeatherSensorDescription(
        key="wind_bearing",
        name="Wind Direction",
        icon="mdi:compass-outline",
        value_fn=lambda data: cast(str, data) if data is not None else None,
    ),
    NOAAWeatherSensorDescription(
        key="native_wind_speed",
        name="Wind Speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(float(data), 2)
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    NOAAWeatherSensorDescription(
        key="native_wind_gust_speed",
        name="Wind Gust",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(float(data), 2)
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    NOAAWeatherSensorDescription(
        key="native_dew_point",
        name="Dew Point",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(float(data), 1)
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    NOAAWeatherSensorDescription(
        key="native_visibility",
        name="Visibility",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(float(data), 1)
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    NOAAWeatherSensorDescription(
        key="short_forecast",
        name="Short Forecast",
        icon="mdi:text-short",
        value_fn=lambda data: cast(str, data) if data is not None else None,
    ),
    NOAAWeatherSensorDescription(
        key="uv_index",
        name="UV Index",
        icon="mdi:weather-sunny-alert",
        native_unit_of_measurement="UV Index",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data)
        if data is not None and isinstance(data, (float, int))
        else (
            int(float(data))
            if data is not None and str(data).replace(".", "", 1).isdigit()
            else None
        ),
    ),
    NOAAWeatherSensorDescription(
        key="cloud_coverage",
        name="Cloud Coverage",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:weather-cloudy",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data)
        if data is not None and isinstance(data, (float, int))
        else (
            int(float(data))
            if data is not None and str(data).replace(".", "", 1).isdigit()
            else None
        ),
    ),
    NOAAWeatherSensorDescription(
        key="timestamp",
        name="Forecast Period Start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-start",
        value_fn=lambda data: dt_util.utc_from_timestamp(float(data))
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
    # New sensor for the actual API data fetch time from noaa_client
    NOAAWeatherSensorDescription(
        key=KEY_LAST_API_UPDATE_FROM_CLIENT,  # Use the constant for the key from forecast data
        name="Last Weather Data Update",  # This will be the sensor's friendly name
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-check-outline",
        value_fn=lambda data: dt_util.utc_from_timestamp(float(data))
        if data is not None and str(data).replace(".", "", 1).isdigit()
        else None,
    ),
)


def _extract_forecast_series(
    coordinator_data: dict[str, Any] | None,
    sensor_key: str,
    forecast_attr: str,
) -> list[dict[str, Any]]:
    """
    Extracts a time series for a given sensor key from the forecast data.
    """
    processed_series_data = []
    if not coordinator_data:
        _LOGGER.info(
            "SENSOR PLATFORM: _extract_forecast_series called with no coordinator_data."
        )
        return []

    list_of_forecast_periods = coordinator_data.get(forecast_attr, [])

    if not isinstance(list_of_forecast_periods, list):
        _LOGGER.info(
            "SENSOR PLATFORM: Forecast data for %s is not a list: %s",
            forecast_attr,
            list_of_forecast_periods,
        )
        return []

    for period_data in list_of_forecast_periods:
        if not isinstance(period_data, dict):
            _LOGGER.info(
                "SENSOR PLATFORM: Forecast period data is not a dict: %s", period_data
            )
            continue

        value = period_data.get(sensor_key)
        datetime_str_for_charting = period_data.get("datetime")

        if value is not None and datetime_str_for_charting is not None:
            processed_series_data.append(
                {"value": value, "datetime": datetime_str_for_charting}
            )
        elif value is not None and sensor_key in [
            "timestamp",
            KEY_LAST_API_UPDATE_FROM_CLIENT,
        ]:
            iso_datetime = None
            if (
                str(value).replace(".", "", 1).isdigit()
            ):  # Check if value is numeric string
                try:
                    iso_datetime = dt_util.utc_from_timestamp(float(value)).isoformat()
                except (ValueError, TypeError):
                    _LOGGER.warning(
                        "SENSOR PLATFORM: Could not convert timestamp value '%s' to datetime for key '%s'",
                        value,
                        sensor_key,
                    )

            processed_series_data.append(
                {"value": value, "datetime": datetime_str_for_charting or iso_datetime}
            )

        elif value is not None and datetime_str_for_charting is None:
            _LOGGER.info(
                "SENSOR PLATFORM: Sensor key '%s' for %s found but 'datetime' missing in period: %s. Value will be orphaned for charting.",
                sensor_key,
                forecast_attr,
                period_data,
            )
    return processed_series_data


class NOAAWeatherSensor(
    CoordinatorEntity[NOAAWeatherDataUpdateCoordinator], SensorEntity
):
    """Define an NOAAWeather entity that holds multiple forecast values."""

    _attr_has_entity_name = False
    entity_description: NOAAWeatherSensorDescription

    def __init__(
        self,
        coordinator: NOAAWeatherDataUpdateCoordinator,
        description: NOAAWeatherSensorDescription,
        forecast_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._forecast_type = forecast_type

        base_name_slug = slugify(coordinator.location_name or "noaa_weather")

        if description.key == KEY_LAST_API_UPDATE_FROM_CLIENT:
            self._attr_name = description.name
            self._attr_unique_id = f"{base_name_slug}_{description.key}"  # No forecast_type in ID for this one
        else:
            self._attr_name = f"{description.name} {self._forecast_type.capitalize()}"
            self._attr_unique_id = (
                f"{base_name_slug}_{description.key}_{self._forecast_type}"
            )

        self._attr_device_info = coordinator.device_info
        self._sensor_series_data: list[dict[str, Any]] = []
        self._update_sensor_data()

        _LOGGER.info(
            "SENSOR PLATFORM: Initialized Sensor: '%s', Unique ID: '%s', Device: %s",
            self._attr_name,
            self._attr_unique_id,
            self._attr_device_info.get("name") if self._attr_device_info else "None",
        )

    def _update_sensor_data(self) -> None:
        """Update the sensor's series data from the coordinator."""
        forecast_attr_key_to_use = self._forecast_type  # Default to the sensor's type

        if self.entity_description.key == KEY_LAST_API_UPDATE_FROM_CLIENT:
            # For "Last Weather Data Update", prioritize hourly, fallback to daily
            if self.coordinator.data and self.coordinator.data.get(
                ATTR_HOURLY_FORECAST
            ):
                forecast_attr_key_to_use = ATTR_HOURLY_FORECAST
            elif self.coordinator.data and self.coordinator.data.get(
                ATTR_DAILY_FORECAST
            ):
                forecast_attr_key_to_use = ATTR_DAILY_FORECAST
            else:  # Neither available
                _LOGGER.info(
                    "SENSOR PLATFORM: No hourly or daily data for %s.", self.name
                )
                self._sensor_series_data = []
                return
        else:  # For other sensors
            forecast_attr_key_to_use = (
                ATTR_HOURLY_FORECAST
                if self._forecast_type == "hourly"
                else ATTR_DAILY_FORECAST
            )

        if self.coordinator.data:
            self._sensor_series_data = _extract_forecast_series(
                self.coordinator.data,
                self.entity_description.key,
                forecast_attr_key_to_use,
            )
            _LOGGER.info(
                "SENSOR PLATFORM: Updated sensor data for %s (%s using %s): %s items. First item value if any: %s",
                self.name,
                self.entity_description.key,
                forecast_attr_key_to_use.split("_")[0],
                len(self._sensor_series_data),
                self._sensor_series_data[0].get("value")
                if self._sensor_series_data
                else "N/A",
            )
        else:
            _LOGGER.info(
                "SENSOR PLATFORM: _update_sensor_data called for %s but coordinator.data is None.",
                self.name,
            )
            self._sensor_series_data = []

    @property
    def native_value(self) -> StateType:
        """Return the value for the current or next forecast period."""
        if self._sensor_series_data:
            first_period_value = self._sensor_series_data[0].get("value")
            try:
                return self.entity_description.value_fn(first_period_value)
            except (ValueError, TypeError) as e:
                _LOGGER.warning(
                    "SENSOR PLATFORM: Error processing native_value for %s with value '%s': %s",
                    self.name,
                    first_period_value,
                    e,
                )
                return None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return state attributes."""
        if self.entity_description.key in [
            "timestamp",
            KEY_LAST_API_UPDATE_FROM_CLIENT,
        ]:
            source_type = self._forecast_type  # Default
            if self.entity_description.key == KEY_LAST_API_UPDATE_FROM_CLIENT:
                if self.coordinator.data and self.coordinator.data.get(
                    ATTR_HOURLY_FORECAST
                ):
                    source_type = "hourly"
                elif self.coordinator.data and self.coordinator.data.get(
                    ATTR_DAILY_FORECAST
                ):
                    source_type = "daily"
            return {"source_forecast_type": source_type}

        if not self._sensor_series_data:
            return None

        attributes: dict[str, Any] = {
            "forecast_type": self._forecast_type,
            "forecast_data": [],
        }
        forecast_list = []
        for item_data in self._sensor_series_data:
            value = item_data.get("value")
            datetime_str = item_data.get("datetime")
            if value is not None and datetime_str is not None:
                try:
                    processed_value = self.entity_description.value_fn(value)
                    forecast_list.append(
                        {
                            "datetime": datetime_str,
                            "value": processed_value,
                        }
                    )
                except (ValueError, TypeError) as e:
                    _LOGGER.warning(
                        "SENSOR PLATFORM: Error processing attribute value for %s (datetime: %s, value: '%s'): %s",
                        self.name,
                        datetime_str,
                        value,
                        e,
                    )
        attributes["forecast_data"] = forecast_list
        return attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        _LOGGER.info(
            "SENSOR PLATFORM: _handle_coordinator_update received for %s", self.name
        )
        self._update_sensor_data()
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add NOAAWeather entities from a config_entry."""
    _LOGGER.info(
        "SENSOR PLATFORM: async_setup_entry called for config entry ID: %s.",
        config_entry.entry_id,
    )

    coordinator: NOAAWeatherDataUpdateCoordinator | None = hass.data.get(
        DOMAIN, {}
    ).get(config_entry.entry_id)

    if coordinator is None:
        _LOGGER.error(
            "SENSOR PLATFORM: Coordinator not found in hass.data for entry ID %s. Cannot set up sensors.",
            config_entry.entry_id,
        )
        return

    if coordinator.data is None:
        _LOGGER.warning(
            "SENSOR PLATFORM: Coordinator.data is None upon sensor entry setup for %s. Sensors might populate after first successful update.",
            coordinator.location_name,
        )
    else:
        _LOGGER.info(
            "SENSOR PLATFORM: Coordinator data is available for %s. Hourly: %s items. Daily: %s items.",
            coordinator.location_name,
            len(coordinator.data.get(ATTR_HOURLY_FORECAST, []))
            if coordinator.data.get(ATTR_HOURLY_FORECAST) is not None
            else "'NoneType'",
            len(coordinator.data.get(ATTR_DAILY_FORECAST, []))
            if coordinator.data.get(ATTR_DAILY_FORECAST) is not None
            else "'NoneType'",
        )

    sensors_to_add: List[NOAAWeatherSensor] = []
    last_update_sensor_added_flag = (
        False  # To ensure "Last Weather Data Update" is added only once
    )

    # Create HOURLY sensors
    if coordinator.data and isinstance(
        coordinator.data.get(ATTR_HOURLY_FORECAST), list
    ):
        hourly_forecast_data = coordinator.data.get(ATTR_HOURLY_FORECAST, [])
        if hourly_forecast_data and isinstance(hourly_forecast_data[0], dict):
            _LOGGER.info(
                "SENSOR PLATFORM: Hourly forecast data IS present with %d periods for %s. Creating hourly sensors.",
                len(hourly_forecast_data),
                coordinator.location_name,
            )
            first_period_keys_hourly = hourly_forecast_data[0].keys()
            for description in FORECAST_SENSOR_TYPES:
                if description.key == KEY_LAST_API_UPDATE_FROM_CLIENT:
                    if (
                        KEY_LAST_API_UPDATE_FROM_CLIENT in first_period_keys_hourly
                        and not last_update_sensor_added_flag
                    ):
                        sensors_to_add.append(
                            NOAAWeatherSensor(coordinator, description, "hourly")
                        )  # forecast_type is nominal here
                        last_update_sensor_added_flag = True
                        _LOGGER.info(
                            "SENSOR PLATFORM: Queued 'Last Weather Data Update' sensor (from hourly data) for %s.",
                            coordinator.location_name,
                        )
                    continue

                if description.key in first_period_keys_hourly:
                    sensors_to_add.append(
                        NOAAWeatherSensor(coordinator, description, "hourly")
                    )
                    _LOGGER.info(
                        "SENSOR PLATFORM: Queued hourly sensor for %s: %s",
                        coordinator.location_name,
                        description.name,
                    )
                elif description.key != KEY_LAST_API_UPDATE_FROM_CLIENT:
                    _LOGGER.info(
                        "SENSOR PLATFORM: Skipping hourly sensor for %s key '%s'; not in first hourly period keys.",
                        coordinator.location_name,
                        description.key,
                    )
        else:
            _LOGGER.info(
                "SENSOR PLATFORM: Hourly forecast data is empty or first item not a dict for %s. Skipping hourly sensors.",
                coordinator.location_name,
            )
    else:
        _LOGGER.warning(
            "SENSOR PLATFORM: Hourly forecast data (ATTR_HOURLY_FORECAST) is MISSING or not a list for %s. Skipping hourly sensors.",
            coordinator.location_name,
        )

    # Create DAILY sensors
    daily_sensor_keys_of_interest = [
        "condition",
        "native_temperature",
        "native_templow",
        "native_pressure",
        "native_wind_speed",
        "wind_bearing",
        "precipitation_probability",
        "humidity",
        "uv_index",
        "cloud_coverage",
        "short_forecast",
        "timestamp",
        KEY_LAST_API_UPDATE_FROM_CLIENT,
    ]

    if coordinator.data and isinstance(coordinator.data.get(ATTR_DAILY_FORECAST), list):
        daily_forecast_data = coordinator.data.get(ATTR_DAILY_FORECAST, [])
        if daily_forecast_data and isinstance(daily_forecast_data[0], dict):
            _LOGGER.info(
                "SENSOR PLATFORM: Daily forecast data IS present with %d periods for %s. Creating daily sensors.",
                len(daily_forecast_data),
                coordinator.location_name,
            )
            first_period_keys_daily = daily_forecast_data[0].keys()
            for description in FORECAST_SENSOR_TYPES:
                if description.key == KEY_LAST_API_UPDATE_FROM_CLIENT:
                    if (
                        KEY_LAST_API_UPDATE_FROM_CLIENT in first_period_keys_daily
                        and not last_update_sensor_added_flag
                    ):
                        sensors_to_add.append(
                            NOAAWeatherSensor(coordinator, description, "daily")
                        )  # forecast_type is nominal here
                        last_update_sensor_added_flag = True
                        _LOGGER.info(
                            "SENSOR PLATFORM: Queued 'Last Weather Data Update' sensor (from daily data) for %s.",
                            coordinator.location_name,
                        )
                    continue

                if (
                    description.key in daily_sensor_keys_of_interest
                    and description.key in first_period_keys_daily
                ):
                    # Avoid creating duplicate sensors if already added as hourly
                    is_already_added_as_hourly = any(
                        s.entity_description.key == description.key
                        and s._forecast_type == "hourly"
                        for s in sensors_to_add
                    )
                    if not is_already_added_as_hourly or description.key in [
                        "native_templow",
                        "native_temperature",
                    ]:  # Allow temp/templow to be both
                        sensors_to_add.append(
                            NOAAWeatherSensor(coordinator, description, "daily")
                        )
                        _LOGGER.info(
                            "SENSOR PLATFORM: Queued daily sensor for %s: %s",
                            coordinator.location_name,
                            description.name,
                        )
                    elif description.key not in [
                        "native_templow",
                        "native_temperature",
                    ]:
                        _LOGGER.info(
                            "SENSOR PLATFORM: Sensor for key '%s' already added as hourly, skipping daily for %s.",
                            description.key,
                            coordinator.location_name,
                        )

                elif (
                    description.key in daily_sensor_keys_of_interest
                    and description.key != KEY_LAST_API_UPDATE_FROM_CLIENT
                ):
                    _LOGGER.info(
                        "SENSOR PLATFORM: Skipping daily sensor for %s key '%s'; not in first daily period keys.",
                        coordinator.location_name,
                        description.key,
                    )
        else:
            _LOGGER.info(
                "SENSOR PLATFORM: Daily forecast data is empty or first item not a dict for %s. Skipping daily sensors.",
                coordinator.location_name,
            )
    else:
        _LOGGER.warning(
            "SENSOR PLATFORM: Daily forecast data (ATTR_DAILY_FORECAST) is MISSING or not a list for %s. Skipping daily sensors.",
            coordinator.location_name,
        )

    # Final check if the "Last Weather Data Update" sensor could not be added from either source
    if not last_update_sensor_added_flag:
        # Attempt to find the description for the special sensor to log its intended name
        last_update_desc = next(
            (
                d
                for d in FORECAST_SENSOR_TYPES
                if d.key == KEY_LAST_API_UPDATE_FROM_CLIENT
            ),
            None,
        )
        intended_name = (
            last_update_desc.name if last_update_desc else "Last Weather Data Update"
        )
        _LOGGER.warning(
            "SENSOR PLATFORM: Could not create '%s' sensor for %s; key '%s' not found in available hourly or daily forecast data.",
            intended_name,
            coordinator.location_name,
            KEY_LAST_API_UPDATE_FROM_CLIENT,
        )

    if sensors_to_add:
        async_add_entities(sensors_to_add)
        _LOGGER.info(
            "SENSOR PLATFORM: Added %d NOAA weather forecast sensors in total for %s.",
            len(sensors_to_add),
            coordinator.location_name,
        )
    else:
        _LOGGER.info(
            "SENSOR PLATFORM: No NOAA weather forecast sensors were added for %s.",
            coordinator.location_name,
        )
