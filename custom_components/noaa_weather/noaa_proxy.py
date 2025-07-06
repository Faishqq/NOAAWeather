import aiohttp  # Ensure aiohttp is imported for ClientSession type hint
import logging
from typing import Any, Optional

from .noaa_client import NOAAApiForHA  # Assuming noaa_client is in the same directory


class ApiError(Exception):
    """Base class for exceptions raised by an API."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ClientConnectorError(ApiError):
    """Exception for client connector errors."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(f"Client Connector Error: {message}", status_code, response)


class InvalidApiKeyError(ApiError):
    """Exception for invalid API key errors."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(f"Invalid API Key: {message}", status_code, response)


class RequestsExceededError(ApiError):
    """Exception for API requests exceeded errors."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(f"Requests Exceeded: {message}", status_code, response)


class NOAAProxy:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        logger: logging.Logger,
        lat: float,
        lon: float,
        api_key: str | None = None,
        url: str | None = None,
    ):
        self._lat = lat
        self._lon = lon
        self._session = session  # Store the passed session
        self._logger = logger
        self._noaa_url = url
        self._api_key = api_key
        self._noaa_api: NOAAApiForHA

        self._noaa_api = NOAAApiForHA(
            session=self._session,  # Pass the session to NOAAApiForHA
            logger=self._logger,
            lat=self._lat,
            lon=self._lon,
            url=self._noaa_url,
            api_key=self._api_key,
        )

    async def async_get_current_conditions(self) -> dict[str, Any]:
        # This method should ideally fetch actual current conditions.
        # If it's derived from the first hour of the hourly forecast,
        # ensure your noaa_client.NOAAApiForHA.async_get_hourly_forecasts()
        # provides data where the first entry is suitable as "current".
        hourly_forecasts = await self._noaa_api.async_get_hourly_forecasts()
        if hourly_forecasts:
            return hourly_forecasts[0]
        self._logger.warning(
            "NOAA_PROXY: async_get_current_conditions(): No hourly forecast data to derive current conditions."
        )
        return {}

    async def async_get_hourly_forecast(self) -> list[dict[str, Any]]:
        hourly_forecasts = await self._noaa_api.async_get_hourly_forecasts()
        return hourly_forecasts if hourly_forecasts is not None else []

    async def async_get_daily_forecast(self) -> list[dict[str, Any]]:
        daily_forecasts = await self._noaa_api.async_get_daily_forecasts()
        return daily_forecasts if daily_forecasts is not None else []
