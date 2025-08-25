import calendar
from datetime import date, datetime, timezone, tzinfo, timedelta
from typing import Literal, overload, Optional, Union

from dateutil.relativedelta import relativedelta

from recently.duration import Z, SAFE_AWARE_DATETIME_MAX, SAFE_AWARE_DATETIME_MIN

__all__ = (
    "to_datetime",
    "now",
    "naive_now",
    "ago",
    "after",
    "first",
    "last",
    "to_tz",
)


def to_datetime(__date: date, /, tz: tzinfo = timezone.utc) -> datetime:
    return datetime(year=__date.year, month=__date.month, day=__date.day, tzinfo=tz)


def now(tz: tzinfo = timezone.utc, /) -> datetime:
    return datetime.now(tz=tz)


def today(tz: tzinfo = timezone.utc, /) -> date:
    return datetime.now(tz=tz).date()


def naive_now(tz: tzinfo = timezone.utc) -> datetime:
    return now(tz).replace(tzinfo=None)


@overload
def ago(
    __from: datetime,
    /,
    delta: timedelta = ...,
    *,
    days: int = ...,
    seconds: int = ...,
    microseconds: int = ...,
    minutes: int = ...,
    hours: int = ...,
    weeks: int = ...,
    months: int = ...,
    years: int = ...,
    tz: Optional[tzinfo] = ...,
) -> datetime: ...


@overload
def ago(
    __from: date,
    /,
    delta: timedelta = ...,
    *,
    days: int = ...,
    seconds: int = ...,
    microseconds: int = ...,
    minutes: int = ...,
    hours: int = ...,
    weeks: int = ...,
    months: int = ...,
    years: int = ...,
    tz: Optional[tzinfo] = ...,
) -> date: ...


def ago(  # noqa: PLR0913
    __from: Union[datetime, date],
    /,
    delta: timedelta = Z,
    *,
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0,
    months: int = 0,
    years: int = 0,
    tz: Optional[tzinfo] = None,
) -> Union[datetime, date]:
    relative_delta = relativedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
        months=months,
        years=years,
    )

    if isinstance(__from, datetime):
        return __from.astimezone(tz or __from.tzinfo) - delta - relative_delta

    if isinstance(__from, date):
        return (to_datetime(__from, tz) - delta - relative_delta).date()

    raise NotImplementedError(f"Object of type {type(__from)} not supported!")


@overload
def after(
    __from: datetime,
    /,
    delta: timedelta = ...,
    *,
    days: int = ...,
    seconds: int = ...,
    microseconds: int = ...,
    minutes: int = ...,
    hours: int = ...,
    weeks: int = ...,
    months: int = ...,
    years: int = ...,
    tz: Optional[tzinfo] = ...,
) -> datetime: ...


@overload
def after(
    __from: date,
    /,
    delta: timedelta = ...,
    *,
    days: int = ...,
    seconds: int = ...,
    microseconds: int = ...,
    minutes: int = ...,
    hours: int = ...,
    weeks: int = ...,
    months: int = ...,
    years: int = ...,
    tz: Optional[tzinfo] = ...,
) -> date: ...


def after(  # noqa: PLR0913
    __from: Union[datetime, date],
    /,
    delta: timedelta = Z,
    *,
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0,
    months: int = 0,
    years: int = 0,
    tz: Optional[tzinfo] = None,
) -> Union[datetime, date]:
    relative_delta = relativedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
        months=months,
        years=years,
    )

    if isinstance(__from, datetime):
        return __from.astimezone(tz or __from.tzinfo) + delta + relative_delta

    if isinstance(__from, date):
        return (to_datetime(__from, tz) + delta + relative_delta).date()

    raise NotImplementedError(f"Object of type {type(__from)} not supported!")


@overload
def first(__for: datetime, /, *, period: Literal["MONTH", "YEAR"]) -> datetime: ...


@overload
def first(__for: date, /, *, period: Literal["MONTH", "YEAR"]) -> date: ...


def first(
    __for: Union[datetime, date],
    period: Literal["MONTH", "YEAR"],
    /,
) -> Union[datetime, date]:
    if period == "MONTH":
        result = SAFE_AWARE_DATETIME_MIN.replace(
            __for.year, __for.month, tzinfo=__for.tzinfo
        )
    elif period == "YEAR":
        result = SAFE_AWARE_DATETIME_MIN.replace(__for.year, tzinfo=__for.tzinfo)
    else:
        raise NotImplementedError(f"Period {period!r} is not supported!")

    if not isinstance(__for, datetime):
        return result.date()

    return result


@overload
def last(__for: datetime, /, *, period: Literal["MONTH", "YEAR"]) -> datetime: ...


@overload
def last(__for: date, /, *, period: Literal["MONTH", "YEAR"]) -> date: ...


def last(
    __for: Union[datetime, date],
    period: Literal["MONTH", "YEAR"],
    /,
) -> Union[datetime, date]:
    if period == "MONTH":
        _, number_of_days = calendar.monthrange(__for.year, __for.month)
        result = SAFE_AWARE_DATETIME_MAX.replace(
            __for.year,
            __for.month,
            number_of_days,
            tzinfo=__for.tzinfo,
        )
    elif period == "YEAR":
        result = SAFE_AWARE_DATETIME_MAX.replace(__for.year, tzinfo=__for.tzinfo)
    else:
        raise NotImplementedError(f"Period {period!r} is not supported!")

    if not isinstance(__for, datetime):
        return result.date()

    return result


def to_tz(__datetime: datetime, /, *, tz: tzinfo = timezone.utc) -> datetime:
    if __datetime.tzinfo is not None:
        return __datetime.astimezone(tz)
    return __datetime.replace(tzinfo=tz).astimezone(tz)
