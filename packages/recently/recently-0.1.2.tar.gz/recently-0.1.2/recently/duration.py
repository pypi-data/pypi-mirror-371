from datetime import date, datetime, timedelta, timezone
from typing import Final
from zoneinfo import ZoneInfo

__all__ = (
    "HOUR",
    "MINUTE",
    "SECOND",
    "Z",
    "SAFE_AWARE_DATETIME_MAX",
    "NAIVE_DATETIME_MAX",
    "DATE_MAX",
    "SAFE_AWARE_DATETIME_MIN",
    "NAIVE_DATETIME_MIN",
    "DATE_MIN",
    "seconds",
    "minutes",
    "hours",
)

HOUR: Final[timedelta] = timedelta(hours=1)
MINUTE: Final[timedelta] = timedelta(minutes=1)
SECOND: Final[timedelta] = timedelta(seconds=1)
Z: Final[timedelta] = timedelta(seconds=0)
SAFE_AWARE_DATETIME_MAX: Final[datetime] = datetime.max.replace(
    tzinfo=ZoneInfo("Etc/GMT-14")
).astimezone(timezone.utc)
NAIVE_DATETIME_MAX: Final[datetime] = datetime.max
DATE_MAX: Final[date] = date.max
SAFE_AWARE_DATETIME_MIN: Final[datetime] = datetime.min.replace(
    tzinfo=ZoneInfo("Etc/GMT+12")
).astimezone(timezone.utc)
NAIVE_DATETIME_MIN: Final[datetime] = datetime.min
DATE_MIN: Final[date] = date.min


def hours(delta: timedelta) -> float:
    return delta / HOUR


def minutes(delta: timedelta) -> float:
    return delta / MINUTE


def seconds(delta: timedelta) -> float:
    return delta / SECOND
