from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)
from dateutil.relativedelta import relativedelta
from struct import (
    unpack,
    unpack_from,
)

from .nullables import if_nullable


@if_nullable
def to_date(binary_data: bytes) -> date:
    """Unpack date value."""

    default_date = date(2000, 1, 1)

    return default_date + timedelta(
        days=unpack("!i", binary_data)[0]
    )


@if_nullable
def to_timestamp(binary_data: bytes) -> datetime:
    """Unpack timestamp value."""

    default_date = datetime(2000, 1, 1)

    return default_date + timedelta(
        microseconds=unpack("!q", binary_data)[0]
    )


@if_nullable
def to_timestamptz(binary_data: bytes) -> datetime:
    """Unpack timestamptz value."""

    return to_timestamp(binary_data).replace(
        tzinfo=timezone.utc
    )


@if_nullable
def to_time(binary_data: bytes) -> time:
    """Unpack time value."""

    microseconds: int = unpack_from("!q", binary_data)[0]
    seconds, microsecond = divmod(microseconds, 1_000_000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    hours = hours % 24

    return time(
        hour=hours,
        minute=minutes,
        second=seconds,
        microsecond=microsecond,
    )


@if_nullable
def to_timetz(binary_data: bytes) -> time:
    """Unpack timetz value."""

    time_notz: time = to_time(binary_data)
    tz_offset_sec: int = unpack('>i', binary_data[-4:])[0]
    tz_offset = timedelta(seconds=tz_offset_sec)

    return time_notz.replace(tzinfo=timezone(tz_offset))


@if_nullable
def to_interval(binary_data: bytes) -> relativedelta:
    """Unpack interval value."""

    microseconds, days, months = unpack('>qii', binary_data)

    return relativedelta(
        months=months,
        days=days,
        microseconds=microseconds
    )
