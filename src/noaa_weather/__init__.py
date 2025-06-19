"""The NOAA Weather integration."""

from __future__ import annotations

from datetime import timedelta, datetime  # Added datetime
import logging
from typing import Any, Optional

from aiohttp.client import ClientSession
from async_timeout import timeout
from zoneinfo import ZoneInfo  # For timezone-aware datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util  # For timezone utilities

from . import noaa_proxy
from .const import (
    ATTR_CURRENT_CONDITION,
    ATTR_DAILY_FORECAST,
    ATTR_HOURLY_FORECAST,
    CONF_TRACK_HOME,
    DOMAIN,
    DEFAULT_HOME_LATITUDE,
    DEFAULT_HOME_LONGITUDE,
    MANUFACTURER,
    NOAA_UPDATE_INTERVAL_MIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.WEATHER]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up NOAA Weather from a config entry."""
    _LOGGER.info(
        "INIT.PY: async_setup_entry called for entry ID: %s", config_entry.entry_id
    )

    clean_location_name = (
        config_entry.data.get(CONF_NAME) or config_entry.title or "NOAA Weather"
    )
    _LOGGER.info("INIT.PY: Determined clean location name: %s", clean_location_name)

    api_key = config_entry.data.get(CONF_API_KEY)

    home_latitude = (
        hass.config.latitude
        if hass.config.latitude is not None
        else DEFAULT_HOME_LATITUDE
    )
    home_longitude = (
        hass.config.longitude
        if hass.config.longitude is not None
        else DEFAULT_HOME_LONGITUDE
    )
    latitude = config_entry.data.get(CONF_LATITUDE, home_latitude)
    longitude = config_entry.data.get(CONF_LONGITUDE, home_longitude)

    _LOGGER.info("INIT.PY: API Key: %s", "REDACTED" if api_key else "None")
    _LOGGER.info("INIT.PY: Using latitude: %s, longitude: %s", latitude, longitude)

    websession = async_get_clientsession(hass)
    _LOGGER.info("INIT.PY: WebSession obtained.")
    _LOGGER.info(
        "INIT.PY: Creating UpdateCoordinator with location name: %s",
        clean_location_name,
    )

    coordinator = NOAAWeatherDataUpdateCoordinator(
        hass,
        websession,
        api_key,
        latitude,
        longitude,
        clean_location_name,
        config_entry,
    )
    _LOGGER.info("INIT.PY: Coordinator created.")

    _LOGGER.info("INIT.PY: Attempting coordinator.async_config_entry_first_refresh()")
    try:
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.info(
            "INIT.PY: coordinator.async_config_entry_first_refresh() SUCCEEDED."
        )
    except Exception as e:
        _LOGGER.error(
            "INIT.PY: coordinator.async_config_entry_first_refresh() FAILED: %s",
            e,
            exc_info=True,
        )

    _LOGGER.info("INIT.PY: Setting up update listener for config entry.")
    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    _LOGGER.info("INIT.PY: Storing coordinator in hass.data.")
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator
    # Keep previous log level for coordinator data
    _LOGGER.debug(
        "INIT.PY: Coordinator data after first refresh: %s",
        coordinator.data
        if _LOGGER.isEnabledFor(logging.DEBUG)
        else "Enable DEBUG for full data",
    )

    _LOGGER.info(
        "INIT.PY: Preparing to forward entry setups to platforms: %s", PLATFORMS
    )
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    _LOGGER.info("INIT.PY: Finished forwarding entry setups.")

    _LOGGER.info("INIT.PY: NOAA Weather setup, END")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info(
        "INIT.PY: NOAA Weather async_unload_entry(), START for entry ID: %s",
        entry.entry_id,
    )
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.info(
            "INIT.PY: Successfully unloaded platforms and removed coordinator from hass.data."
        )
    else:
        _LOGGER.warning(
            "INIT.PY: Failed to unload one or more platforms for entry ID: %s",
            entry.entry_id,
        )

    _LOGGER.info("INIT.PY: NOAA Weather async_unload_entry(), END")
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    _LOGGER.info(
        "INIT.PY: NOAA Weather update_listener() called for entry ID: %s. Reloading entry.",
        entry.entry_id,
    )
    await hass.config_entries.async_reload(entry.entry_id)
    _LOGGER.info("INIT.PY: NOAA Weather update_listener(), END")


class NOAAWeatherDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching NOAA weather data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        api_key: Optional[str],
        lat: float,
        lon: float,
        location_name: str,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.location_name = location_name
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.session = session
        self.last_api_update: datetime | None = None  # Initialize last update time

        _LOGGER.info(
            "COORDINATOR: Initializing for location: %s at (%s, %s)",
            self.location_name,
            lat,
            lon,
        )

        self.noaaproxy = noaa_proxy.NOAAProxy(
            session=self.session,  # Corrected order from user's file
            logger=_LOGGER,
            lat=self.lat,
            lon=self.lon,
            api_key=self.api_key,  # Corrected order
            url=None,  # url is optional in NOAAProxy
        )

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.location_name,
            manufacturer=MANUFACTURER,
            model="Weather Station Data",
            configuration_url=(f"https://api.weather.gov/points/{lat},{lon}"),
        )

        update_interval = timedelta(minutes=NOAA_UPDATE_INTERVAL_MIN)
        _LOGGER.info(
            "COORDINATOR: Update interval set to %s for %s",
            update_interval,
            self.location_name,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {self.location_name}",
            update_interval=update_interval,
        )
        _LOGGER.info(
            "COORDINATOR: NOAAWeatherDataUpdateCoordinator initialization complete for %s.",
            self.location_name,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        _LOGGER.info(
            "COORDINATOR: _async_update_data() called for %s", self.location_name
        )
        current: dict[str, Any] = {}
        daily_forecast: list[dict[str, Any]] = []
        hourly_forecast: list[dict[str, Any]] = []
        try:
            async with timeout(20):  # Increased timeout slightly
                _LOGGER.info(  # Changed to INFO
                    "COORDINATOR: Fetching current conditions for %s...",
                    self.location_name,
                )
                current = await self.noaaproxy.async_get_current_conditions()
                _LOGGER.info(  # Changed to INFO
                    "COORDINATOR: Fetching daily forecast for %s...", self.location_name
                )
                daily_forecast = await self.noaaproxy.async_get_daily_forecast()
                _LOGGER.info(  # Changed to INFO
                    "COORDINATOR: Fetching hourly forecast for %s...",
                    self.location_name,
                )
                hourly_forecast = await self.noaaproxy.async_get_hourly_forecast()

                # If all fetches are successful, update the timestamp
                self.last_api_update = dt_util.utcnow()  # Use HA's timezone utility
                _LOGGER.info(
                    "COORDINATOR: Data fetched successfully for %s at %s. Current: %s, Daily: %d items, Hourly: %d items",
                    self.location_name,
                    self.last_api_update.isoformat(),  # Log the update time
                    "data available" if current else "no data",
                    len(daily_forecast) if daily_forecast is not None else 0,
                    len(hourly_forecast) if hourly_forecast is not None else 0,
                )
        except noaa_proxy.InvalidApiKeyError as error:
            _LOGGER.error(
                "COORDINATOR: Invalid API Key for %s. Error: %s",
                self.location_name,
                error,
            )
            raise UpdateFailed(f"Invalid API Key: {error}") from error
        except noaa_proxy.ClientConnectorError as error:
            _LOGGER.error(
                "COORDINATOR: Client connector error for %s: %s",
                self.location_name,
                error,
                exc_info=True,
            )
            raise UpdateFailed(f"Client connector error: {error}") from error
        except noaa_proxy.ApiError as error:
            _LOGGER.error(
                "COORDINATOR: API error for %s: %s",
                self.location_name,
                error,
                exc_info=True,
            )
            raise UpdateFailed(f"API error: {error}") from error
        except TimeoutError:
            _LOGGER.error(
                "COORDINATOR: Timeout fetching data for %s", self.location_name
            )
            raise UpdateFailed(
                f"Timeout communicating with API for {self.location_name}"
            ) from TimeoutError
        except Exception as error:
            _LOGGER.error(
                "COORDINATOR: Unexpected error updating data for %s: %s",
                self.location_name,
                error,
                exc_info=True,
            )
            raise UpdateFailed(
                f"Unexpected error communicating with API: {error}"
            ) from error

        result_data = {
            ATTR_CURRENT_CONDITION: current if current is not None else {},
            ATTR_DAILY_FORECAST: daily_forecast if daily_forecast is not None else [],
            ATTR_HOURLY_FORECAST: hourly_forecast
            if hourly_forecast is not None
            else [],
        }
        _LOGGER.info(
            "COORDINATOR: _async_update_data() for %s is returning. Hourly forecast contains %d items.",
            self.location_name,
            len(result_data[ATTR_HOURLY_FORECAST]),
        )
        # Keep previous log level for full data
        _LOGGER.debug(
            "COORDINATOR: Full data for %s: %s",
            self.location_name,
            result_data
            if _LOGGER.isEnabledFor(logging.DEBUG)
            else "Enable DEBUG for full data",
        )
        return result_data
