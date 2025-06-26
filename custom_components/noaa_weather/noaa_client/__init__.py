"""NOAA Weather Package."""

import logging
import time
from typing import Any

import aiohttp

from . import const, daily_forecast, hourly_forecast


class NOAAApiForHA:
    """The main class for Home Assistant to access NOAA weather data."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        logger: logging.Logger,
        lat: float = const.DEFAULT_LAT,
        lon: float = const.DEFAULT_LON,
        url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the NOAAApiForHA object."""
        self._lat: float = lat
        self._lon: float = lon
        self._url = url
        if self._url is None:
            self._url = const.DEFAULT_NOAA_METADATA_URL
        self._api_key = api_key
        self._session = session
        self._logger = logger
        self._refresh_interval = const.DEFAULT_REFRESH_INTERVAL
        self._metadata: dict[str, Any] = None
        self._metadata_at: float = 0.0
        self._forecast: dict[str, Any] = None
        self._forecast_at: float = 0.0
        self._daily: daily_forecast.DailyForecast = None
        self._forecast_hourly: dict[str, Any] = None
        self._forecast_hourly_at: float = 0.0
        self._hourly: hourly_forecast.HourlyForecast = None
        self._forecast_grid_data: dict[str, Any] = None
        self._forecast_grid_data_at: float = 0.0
        self._all_data_ok: bool = False
        self._all_data_ok_at: float = 0.0

    def set_refresh_interval(self, refresh_interval: float) -> None:
        """Set the refresh interval for data updates."""
        self._refresh_interval = refresh_interval
        self._refresh_interval = max(self._refresh_interval, const.MIN_REFRESH_INTERVAL)

    async def _async_get_url(self, url: str) -> dict[str, Any] | None:
        """Asynchronously retrieve data from a given URL."""
        if not url:
            return None
        try:
            async with self._session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                self._logger.error(
                    "NOAA_API_FOR_HA: Error fetching URL %s: %s", url, response.status
                )
        except Exception as ex:  # noqa: BLE001
            self._logger.error("NOAA_API_FOR_HA: While reading: %s, error: %s", url, ex)
        return None

    async def _async_get_forecasts(self) -> bool:
        """Asynchronously retrieve all forecasts with links in metadata."""
        if not self._metadata:
            return False
        result = True
        url = self._metadata.get(const.META_PROPERTIES, {}).get(const.META_FORECAST)
        response = await self._async_get_url(url)
        if response:
            self._forecast = response
            self._forecast_at = time.time()
            self._daily = daily_forecast.DailyForecast(response, time.time())
        else:
            result = False
        url = self._metadata.get(const.META_PROPERTIES, {}).get(
            const.META_FORECAST_HOURLY
        )
        response = await self._async_get_url(url)
        if response:
            self._forecast_hourly = response
            self._forecast_hourly_at = time.time()
            self._hourly = hourly_forecast.HourlyForecast(response, time.time())
        else:
            result = False
        url = self._metadata.get(const.META_PROPERTIES, {}).get(
            const.META_FORECAST_GRID_DATA
        )
        response = await self._async_get_url(url)
        if response:
            self._forecast_grid_data = response
            self._forecast_grid_data_at = time.time()
        else:
            result = False
        return result

    async def async_get_for_location(
        self, lat: float | None = None, lon: float | None = None
    ) -> bool:
        """Asynchronously retrieve weather data for a given location."""
        try:
            if not lat:
                lat = self._lat
            if not lon:
                lon = self._lon
            lats = (const.LAT_LON_TO_STR % lat).strip()
            lons = (const.LAT_LON_TO_STR % lon).strip()
            url = self._url.format(lat=lats, lon=lons)
            response = await self._async_get_url(url)
            if response:
                self._metadata = response
                self._metadata_at = time.time()
                self._lat = lat
                self._lon = lon
                self._all_data_ok = await self._async_get_forecasts()
                if self._all_data_ok:
                    self._all_data_ok_at = time.time()
                return self._all_data_ok
        except Exception as ex:  # noqa: BLE001
            self._logger.error(
                "NOAA_API_FOR_HA: retreiving weather for location: %s", ex
            )
        return False

    async def async_refresh(self) -> bool:
        """Asynchronously refresh weather data if needed."""
        if self._all_data_ok and (
            time.time() - self._all_data_ok_at < self._refresh_interval
        ):
            return True
        return await self.async_get_for_location()

    async def async_get_daily_forecasts(self) -> list[dict[str, any]]:
        """Asynchronously retrieve daily forecasts."""
        await self.async_refresh()
        if self._daily:
            return self._daily.get_forecast()
        return []

    async def async_get_hourly_forecasts(self):
        """Asynchronously retrieve hourly forecasts."""
        await self.async_refresh()
        if self._hourly:
            return self._hourly.get_forecast()
        return []
