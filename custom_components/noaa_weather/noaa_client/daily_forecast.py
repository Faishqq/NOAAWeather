"""Twice Daily weather forecast for NOAA Weather."""

import time
import traceback
from typing import Any, Final, Required, TypedDict, final

from . import const
from . import noaa_utils


class Forecast(TypedDict, total=False):
    number: Required[int]
    datetime: Required[str]
    is_daytime: bool | None
    timestamp: float | None
    start_time: str | None
    end_time: str | None
    name: str | None
    condition: str | None
    humidity: float | None
    precipitation_probability: int | None
    cloud_coverage: int | None
    native_precipitation: float | None
    native_precipitation_unit: str | None = None
    native_pressure: float | None
    native_pressure_unit: str | None = None
    native_temperature: float | None
    native_temperature_unit: str | None = None
    native_templow: float | None
    native_apparent_temperature: float | None
    wind_bearing: float | str | None
    native_wind_gust_speed: float | None
    native_wind_speed: float | None
    wind_bearing: float | str
    native_dew_point: float | None
    native_visibility: float | None = None
    native_visibility_unit: str | None = None
    short_forecast: str | None
    uv_index: float | None
    icon: str | None


class DailyForecast:
    def __init__(
        self, daily_forecast: list[dict[str:any]], timestamp: float = time.time()
    ):
        self._forecast: dict[str, Any] = daily_forecast
        self._forecast_at: float = timestamp
        self._data: list[Forecast] = []
        self._parse()

    def _parse_period(self, period: dict[str, any]):
        forecast = Forecast(datetime=period.get(const.NOAA_ATTR_DATETIME))
        forecast[const.FORECAST_ATTR_NUMBER] = period.get(const.NOAA_ATTR_NUMBER)
        forecast[const.FORECAST_ATTR_IS_DAYTIME] = period.get(
            const.NOAA_ATTR_IS_DAYTIME
        )
        forecast[const.FORECAST_LAST_API_UPDATE] = (
            self._forecast_at
        )  # set last API update with time the API was successfuly called
        forecast[const.FORECAST_ATTR_TIMESTAMP] = noaa_utils.iso_to_float_time(
            period.get(const.NOAA_ATTR_TIMESTAMP)
        )
        forecast[const.FORECAST_ATTR_START_TIME] = period.get(
            const.NOAA_ATTR_START_TIME
        )
        forecast[const.FORECAST_ATTR_END_TIME] = period.get(const.NOAA_ATTR_END_TIME)
        forecast[const.FORECAST_ATTR_NAME] = period.get(const.NOAA_ATTR_NAME)
        forecast[const.FORECAST_ATTR_CONDITION] = period.get(const.NOAA_ATTR_CONDITION)
        forecast[const.FORECAST_ATTR_HUMIDITY] = None
        try:
            value = float(period.get(const.NOAA_ATTR_NATIVE_TEMPERATURE))
            unit = period.get(const.NOAA_ATTR_NATIVE_TEMPERATURE_UNIT)
            if const.NOAA_UNIT_TEMP_F in unit:
                value = noaa_utils.convert_F_to_C(value)
            forecast[const.FORECAST_ATTR_NATIVE_TEMPERATURE] = value
        except (ValueError, TypeError):
            forecast[const.FORECAST_ATTR_NATIVE_TEMPERATURE] = None
        forecast[const.FORECAST_ATTR_NATIVE_TEMPERATURE_UNIT] = const.CELSIUS
        try:
            forecast[const.FORECAST_ATTR_PRECIPITATION_PROBABILITY] = int(
                period.get(const.NOAA_ATTR_PRECIPITATION_PROBABILITY).get(
                    const.META_VALUE
                )
            )
        except (ValueError, TypeError):
            forecast[const.FORECAST_ATTR_PRECIPITATION_PROBABILITY] = 0
        try:
            value = period.get(const.NOAA_ATTR_NATIVE_WIND_SPEED)
            items = value.split()
            value = float(items[0])
            if const.NOAA_UNIT_MPH in items:
                value = noaa_utils.speed_miph_to_mps(value)
            forecast[const.FORECAST_ATTR_NATIVE_WIND_SPEED] = value
        except (ValueError, TypeError):
            forecast[const.FORECAST_ATTR_NATIVE_WIND_SPEED] = None
        forecast[const.FORECAST_ATTR_WIND_BEARING] = period.get(
            const.NOAA_ATTR_WIND_BEARING
        )
        forecast[const.FORECAST_ATTR_ICON] = period.get(const.NOAA_ATTR_ICON)
        return forecast

    def _parse(self):
        if not self._forecast:
            return
        self._data = []
        try:
            for period in self._forecast.get("properties").get("periods"):
                # print(period)
                forecast = self._parse_period(period)
                self._data.append(forecast)
        except Exception:
            traceback.print_exc()

    def get_forecast(self) -> list[dict[str, Any]]:
        return self._data
