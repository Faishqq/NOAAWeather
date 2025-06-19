"""Constants used in NOAA Weather API."""

MIN_REFRESH_INTERVAL = 1800.0  # do not spam NOAA server
DEFAULT_REFRESH_INTERVAL = 3600.0 * 12.0
DEFAULT_NOAA_METADATA_URL = "https://api.weather.gov/points/{lat},{lon}"
DEFAULT_LAT = 37.3611
DEFAULT_LON = -121.9278
LAT_LON_TO_STR = "%9.4f"

META_PROPERTIES = "properties"
META_FORECAST = "forecast"
META_FORECAST_HOURLY = "forecastHourly"
META_FORECAST_GRID_DATA = "forecastGridData"
META_VALUES = "values"
META_TIME = "validTime"
META_VALUE = "value"
META_UNIT = "unitCode"


DATA_UNIT_KEY = "uom"
DATA_UNIT_SEPARATOR = ":"

DATA_UNIT_PERCENT = "percent"
DATA_UNIT_PERCENT_RENAME = "%"
DATA_UNIT_DIRECTION = "degree_(angle)"
DATA_UNIT_DIRECTION_RENAME = "deg"
DATA_UNIT_SPEED = "km_h-1"
DATA_UNIT_SPEED_RENAME = "km/h"

NOAA_UNIT_DEG_C = "degC"
NOAA_UNIT_DEG_F = "degF"
NOAA_UNIT_TEMP_F = "F"
NOAA_UNIT_MPH = "mph"


CELSIUS = "°C"
MILLIMETERS = "mm"
METERS = "m"
KILOMETERS = "km"
METERS_PER_SECOND = "m/s"
KILOMETERS_PER_HOUR = "km/h"
PA = "Pa"


META_TIME_ZONE = "UTC"  # NOAA Data Time zone

META_GRID_TEMPERATURE = "temperature"
META_GRID_DEWPOINT = "dewpoint"
META_GRID_MAX_TEMPERATURE = "maxTemperature"
META_GRID_MIN_TEMPERATURE = "minTemperature"
META_GRID_RELATIVE_HUMIDITY = "relativeHumidity"
META_GRID_APPARENT_TEMPERATURE = "apparentTemperature"
META_GRID_WBGT = "wetBulbGlobeTemperature"
META_GRID_HEAT_INDEX = "heatIndex"
META_GRID_WIND_CHILL = "windChill"
META_GRID_SKY_COWER = "skyCover"  # percent
META_GRID_WIND_DIRECTION = "windDirection"  # degree_(angle)
META_GRID_WIND_SPEED = "windSpeed"  # km_h-1
META_GRID_WIND_GUST = "windGust"  # km_h-1
META_GRID_WEATHER = "weather"  # path: weather/values/value -> parameteric weather description in fields of value
META_GRID_HAZARDS = "hazards"
META_GRID_PROBABILITY_OF_PERCIPITATION = "probabilityOfPrecipitation"  # percent
META_GRID_QUANTITATIVEPERCIPITATION = "quantitativePrecipitation"  # mm
META_GRID_ICE_ACCUMULATION = "iceAccumulation"  # mm
META_GRID_SNOWFALL_AMOUNT = "snowfallAmount"  # mm
META_GRID_SNOWFALL_LEVEL = "snowLevel"  # m  (= altitude of snowfall)
META_GRID_CEILING_HEIGHT = "ceilingHeight"  # m
META_GRID_VISIBILITY = "visibility"
META_GRID_TRANSPORT_WIND_SPEED = "transportWindSpeed"  # km_h-1
META_GRID_MIXING_HEIGHT = "mixingHeight"  # m
META_GRID_LIGHTING_ACTIVITY_LEVEL = "lightningActivityLevel"
META_GRID_20_FT_WIND_SPEED = "twentyFootWindSpeed"  # km_h-1
META_GRID_20_FT_WIND_DIRECTION = "twentyFootWindDirection"  # degree_(angle)
META_GRID_PROBABILITY_OF_THUNDER = "probabilityOfThunder"

META_FORECAST_PERIODS = "periods"  # FULL FORECAST FOR A PERIOOD

META_FORECAST_H_PERIODS = "periods"  # hourly forecast. see properties.units and other meta info at properties level which apply to all periods
# keys in periods structure are mostly the same as in META_GRID_* with some exceptions like: "temperatureUnit": "F",
# durarion of a period is explicit:
# "startTime": "2024-09-17T20:00:00-07:00",
# "endTime": "2024-09-17T21:00:00-07:00",


FORECAST_ATTR_NUMBER = "number"
FORECAST_ATTR_DATETIME = "datetime"
FORECAST_ATTR_IS_DAYTIME = "is_daytime"
FORECAST_ATTR_TIMESTAMP = "timestamp"
FORECAST_ATTR_START_TIME = "start_time"
FORECAST_ATTR_END_TIME = "end_time"
FORECAST_ATTR_NAME = "name"
FORECAST_ATTR_CONDITION = "condition"
FORECAST_ATTR_HUMIDITY = "humidity"
FORECAST_ATTR_PRECIPITATION_PROBABILITY = "precipitation_probability"
FORECAST_ATTR_CLOUD_COVERAGE = "cloud_coverage"
FORECAST_ATTR_NATIVE_PRECIPITATION = "native_precipitation"
FORECAST_ATTR_NATIVE_PRECIPITATION_UNIT = "native_precipitation_unit"
FORECAST_ATTR_NATIVE_PRESSURE = "native_pressure"
FORECAST_ATTR_NATIVE_PRESSURE_UNIT = "native_pressure_unit"
FORECAST_ATTR_NATIVE_TEMPERATURE = "native_temperature"
FORECAST_ATTR_NATIVE_TEMPERATURE_UNIT = "native_temperature_unit"
FORECAST_ATTR_NATIVE_TEMPLOW = "native_templow"
FORECAST_ATTR_NATIVE_APPARENT_TEMPERATURE = "native_apparent_temperature"
FORECAST_ATTR_WIND_BEARING = "wind_bearing"
FORECAST_ATTR_NATIVE_WIND_GUST_SPEED = "native_wind_gust_speed"
FORECAST_ATTR_NATIVE_WIND_SPEED = "native_wind_speed"
FORECAST_ATTR_WIND_BEARING = "wind_bearing"
FORECAST_ATTR_NATIVE_DEW_POINT = "native_dew_point"
FORECAST_ATTR_NATIVE_VISIBILITY = "native_visibility"
FORECAST_ATTR_NATIVE_VISIBILITY_UNIT = "native_visibility_unit"
FORECAST_ATTR_SHORT_FORECAST = "short_forecast"
FORECAST_ATTR_UV_INDEX = "uv_index"
FORECAST_ATTR_ICON = "icon"
FORECAST_LAST_API_UPDATE = "last_api_update"

NOAA_ATTR_NUMBER = "number"
NOAA_ATTR_DATETIME = "startTime"
NOAA_ATTR_IS_DAYTIME = "isDaytime"
NOAA_ATTR_TIMESTAMP = "startTime"
NOAA_ATTR_START_TIME = "startTime"
NOAA_ATTR_END_TIME = "endTime"
NOAA_ATTR_NAME = "name"
NOAA_ATTR_CONDITION = "shortForecast"
NOAA_ATTR_HUMIDITY = "relativeHumidity"
NOAA_ATTR_PRECIPITATION_PROBABILITY = "probabilityOfPrecipitation"
NOAA_ATTR_CLOUD_COVERAGE = "cloud_coverage"
NOAA_ATTR_NATIVE_PRECIPITATION = ""
NOAA_ATTR_NATIVE_PRECIPITATION_UNIT = "probabilityOfPrecipitation"
NOAA_ATTR_NATIVE_PRESSURE = "native_pressure"
NOAA_ATTR_NATIVE_PRESSURE_UNIT = "native_pressure_unit"
NOAA_ATTR_NATIVE_TEMPERATURE = "temperature"
NOAA_ATTR_NATIVE_TEMPERATURE_UNIT = "temperatureUnit"
NOAA_ATTR_NATIVE_TEMPLOW = "native_templow"
NOAA_ATTR_NATIVE_APPARENT_TEMPERATURE = "native_apparent_temperature"
NOAA_ATTR_WIND_BEARING = "wind_bearing"
NOAA_ATTR_NATIVE_WIND_GUST_SPEED = "native_wind_gust_speed"
NOAA_ATTR_NATIVE_WIND_SPEED = "windSpeed"
NOAA_ATTR_WIND_BEARING = "windDirection"
NOAA_ATTR_NATIVE_DEW_POINT = "dewpoint"
NOAA_ATTR_NATIVE_VISIBILITY = "native_visibility"
NOAA_ATTR_NATIVE_VISIBILITY_UNIT = "native_visibility_unit"
NOAA_ATTR_SHORT_FORECAST = "short_forecast"
NOAA_ATTR_UV_INDEX = "uv_index"
NOAA_ATTR_ICON = "icon"
NOAA_LAST_API_UPDATE = "last_api_update"
