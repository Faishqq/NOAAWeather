"""Various uitilities used in NOAA Weather.
"""
import re
import sys
import time
import traceback
from datetime import datetime, tzinfo, timedelta
from zoneinfo import ZoneInfo

from typing import Any, Optional, Tuple

# Time utilities

def float_to_iso_time(timestamp: float, timezone: str = None) -> str:
  """Converts a float timestamp to an ISO 8601 time string.

  Args:
    timestamp: The float timestamp.
    timezone: The timezone to use for the time string. Defaults to the local timezone.

  Returns:
    The ISO 8601 time string.
  """

  if not timestamp:
    timestamp = time.time()

  if timezone:
    tz = ZoneInfo(timezone)
  else:
    tz = ZoneInfo('localtime')
  dt = datetime.fromtimestamp(timestamp, tz=tz)
  return dt.isoformat()

def iso_to_float_time(iso_time: str, timezone: str = None) -> float:
  """Converts an ISO 8601 time string to a float timestamp.

  Args:
    iso_time: The ISO 8601 time string.
    timezone: The timezone to use for the time string. Defaults to UTC.

  Returns:
    The float timestamp.
  """

  if not iso_time:
    return 0.0
  if timezone:
    tz = ZoneInfo(timezone)
  else:
    tz = ZoneInfo('localtime')
  dt = datetime.fromisoformat(iso_time)
  if timezone:
    dt = dt.astimezone(tz)
  return dt.timestamp()

def iso_to_float_time_and_delta(iso_time: str, timezone: str = None) -> tuple[float, float | None]:
  """Converts an ISO 8601 time string to a float timestamp and time period.

  Args:
    iso_time: The ISO 8601 time string.
    timezone: The timezone to use for the time string. Defaults to UTC.

  Returns:
    A tuple containing the float timestamp and the time period (as a timedelta object) if specified,
    or None if no time period is specified.
  """

  # Extract the time period if present
  # match = re.match(r"^(.+)/P(\d+H|\d+M|\d+S)$", iso_time)   # does not find match ??
  match = re.match(r"^(.+)/PT(.+)$", iso_time)
  if match:
    iso_time, period_str = match.groups()
  else:
    iso_time = iso_time.split('/')[0]
    period_str = None

  # Convert the ISO time string to a datetime object
  dt = datetime.fromisoformat(iso_time)

  # Apply the timezone if specified
  if timezone:
    dt = dt.astimezone(ZoneInfo(timezone))

  # Convert the time period string to a timedelta object
  time_period = timedelta(seconds=0)
  if period_str:
    if period_str.endswith("H"):
      hours = int(period_str[:-1])
      time_period = timedelta(hours=hours)
    elif period_str.endswith("M"):
      minutes = int(period_str[:-1])
      time_period = timedelta(minutes=minutes)
    elif period_str.endswith("S"):
      seconds = int(period_str[:-1])
      time_period = timedelta(seconds=seconds)

  return dt.timestamp(), time_period.total_seconds()  


#  Temperature conversions

def convert_F_to_C(temperature: float) -> float:
  return (int(((temperature - 32) * 5/9) * 100.0))/ 100.0

def convert_C_to_F(temperature: float) -> float:  
  return int(((temperature * 9.0/5.0) + 32) * 100) / 100.0


# Speed conversions
def speed_miph_to_mps(speed: Any) -> float:
  if not speed:
    return 0.0
  if isinstance(speed, str):
    try:
      speed = float(speed)
    except ValueError:
      speed = 0
  if isinstance(speed, (int, float)):
    return float(speed / 2.237)
  return 0.0

def speed_mps_to_miph(speed: Any) -> float:
  if not speed:
    return 0.0
  if isinstance(speed, str):
    try:
      speed = float(speed)
    except ValueError:
      speed = 0
  if isinstance(speed, (int, float)):
    return float(speed * 2.237)
  return 0.0
