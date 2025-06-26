"""Extract weather grid data.
"""

from typing import Any, Optional

from . import noaa_utils
from . import const

class GridWeather():

  def __init__(self, noaa_grid_data: dict[str, Any]):
    self._forecast_grid_data = noaa_grid_data

  def _find_in_gridpoints(self, what: str = const.META_GRID_TEMPERATURE, when: float = None) -> Optional[str]:
    if not when:
      when = time.time()
    result = None
    values = self._forecast_grid_data.get(const.META_PROPERTIES).get(what).get(const.META_VALUES)
    for value in values:
      time_str = value.get(const.META_TIME)   # .split('/')[0] # strip-off duration
      interval_start, dt = noaa_utils.iso_to_float_time_and_delta(time_str, const.META_TIME_ZONE)
      if interval_start >= when or interval_start + dt > when:
        break
      result = value.get(const.META_VALUE)
    return result

  def _get_temp(self, key: str = const.META_GRID_TEMPERATURE, when: float = None) -> Optional[Tuple[float, str, str]]:
    if not self.refresh():
      return None
    temperature_f = None
    temperature_s = self._find_in_gridpoints(key, when)
    if temperature_s:
      temperature_f = float(int(float(temperature_s) * 100.0))/100.0
    temperature_unit = self._forecast_grid_data.get(const.META_PROPERTIES).get(key).get(DATA_UNIT_KEY)
    if temperature_unit:
      temperature_unit = temperature_unit.split(DATA_UNIT_SEPARATOR)[1].lstrip('deg')
    return temperature_f, temperature_unit, key

  def get_temperature(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_temp(const.META_GRID_TEMPERATURE, when)

  def get_dewpoint(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_temp(const.META_GRID_DEWPOINT, when)

  def get_max_temperature(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_temp(const.META_GRID_MAX_TEMPERATURE, when)

  def get_min_temperature(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_temp(const.META_GRID_MIN_TEMPERATURE, when)

  def get_apparent_temperature(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_temp(const.META_GRID_APPARENT_TEMPERATURE, when)

  def get_wbg_temperature(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_temp(const.META_GRID_WBGT, when)

  def get_heat_index(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_temp(const.META_GRID_HEAT_INDEX, when)

  def get_wind_chill(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_temp(const.META_GRID_WIND_CHILL, when)

  def _get_int_data(self, key: str = const.META_GRID_RELATIVE_HUMIDITY, when: float = None) -> Optional[Tuple[float, str, str]]:
    """Retrieves integer data as float."""
    if not self.refresh():
      return None
    result_f = None
    data_s = self._find_in_gridpoints(key, when)
    if data_s:
      result_f = float(data_s.split('.')[0])    # drop any decimal part
    data_unit = self._forecast_grid_data.get(const.META_PROPERTIES).get(key).get(DATA_UNIT_KEY)
    if data_unit:
      data_unit = temperature_unit.split(DATA_UNIT_SEPARATOR)[1]
      if data_unit == DATA_UNIT_PERCENT:
        data_unit = DATA_UNIT_PERCENT_RENAME
      elif data_unit == DATA_UNIT_DIRECTION:
        data_unit = DATA_UNIT_DIRECTION_RENAME
    return result_f, data_unit, key

  def get_relative_humidity(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_int_data(const.META_GRID_RELATIVE_HUMIDITY, when)

  def get_sky_cover(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_int_data(const.META_GRID_SKY_COWER, when)

  def get_probability_of_precipitation(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_int_data(const.META_GRID_PROBABILITY_OF_PERCIPITATION, when)

  def get_wind_direction(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_int_data(const.META_GRID_WIND_DIRECTION, when)

  def get_20_ft_wind_direction(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_int_data(const.META_GRID_20_FT_WIND_DIRECTION, when)

  def get_probability_of_thunder(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_int_data(const.META_GRID_PROBABILITY_OF_THUNDER, when)

  def get_snow_level(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_int_data(const.META_GRID_SNOWFALL_LEVEL, when)

  def get_lightning_activity_level(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_int_data(const.META_GRID_LIGHTING_ACTIVITY_LEVEL, when)

  def _get_float_data(self, key: str = const.META_GRID_RELATIVE_HUMIDITY, when: float = None) -> Optional[Tuple[float, str, str]]:
    """Retrieves integer data as float."""
    if not self.refresh():
      return None
    result_f = None
    data_s = self._find_in_gridpoints(key, when)
    if data_s:
      result_f = float(int(float(data_s) * 100.0))/100.0
    data_unit = self._forecast_grid_data.get(const.META_PROPERTIES).get(key).get(DATA_UNIT_KEY)
    if data_unit:
      data_unit = temperature_unit.split(DATA_UNIT_SEPARATOR)[1]
      if data_unit == DATA_UNIT_SPEED:
        data_unit = DATA_UNIT_SPEED_RENAME
    return result_f, data_unit, key

  def get_wind_speed(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_WIND_SPEED, when)

  def get_wind_gust(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_WIND_GUST, when)

  def get_quantitative_precipitation(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_QUANTITATIVEPERCIPITATION, when)

  def get_ice_accumulation(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_ICE_ACCUMULATION, when)

  def get_snowfall_amount(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_SNOWFALL_AMOUNT, when)

  def get_ceiling_height(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_CEILING_HEIGHT, when)

  def get_visibility(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_VISIBILITY, when)

  def get_transport_wind_speed(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_TRANSPORT_WIND_SPEED, when)

  def get_mixing_height(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_MIXING_HEIGHT, when)

  def get_20_ft_wind_speed(self, when: float = None) -> Optional[Tuple[float, str, str]]:
    return self._get_float_data(const.META_GRID_20_FT_WIND_SPEED, when)


  def _to_map(self, grid_item: map[str, Any]):
    pass

  def _to_list(self):
    pass