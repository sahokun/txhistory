import math
from datetime import datetime
from decimal import Decimal

from numpy import ndarray
from pandas import DataFrame
from pytz import timezone


def timestamp_fromdatetime(dt):
    return int(dt.timestamp()) if dt else None


def datetime_fromtimestamp(timestamp):
    return (
        datetime.fromtimestamp(timestamp, tz=timezone("Asia/Tokyo"))
        if timestamp
        else None
    )


def to_decimal(value: str):
    return Decimal(value.replace(",", ""))


def get_rate(symbol: str, date_time: str, rate_df: DataFrame) -> Decimal:
    symbol_lower = symbol.lower()
    rate_by_date_time = rate_df[rate_df["datetime"] == date_time]
    if (
        symbol_lower not in rate_by_date_time
        or rate_by_date_time[symbol_lower].size == 0
    ):
        return "N/A"
    value = rate_by_date_time[symbol_lower].values[0]
    if isinstance(value, ndarray):
        value = value[0]
    if value is None or str(value).lower() == "nan":
        return "N/A"
    # print(rate)
    return to_decimal(str(value))
