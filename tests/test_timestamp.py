import csv  # noqa: E402
import os
import pprint  # noqa: E402
import re  # noqa: E402
import sys
from datetime import datetime, timedelta  # noqa: E402
from decimal import Decimal  # noqa: E402
from itertools import groupby  # noqa: E402
from typing import Dict, List, Literal, MutableSet, TypedDict, TypeGuard  # noqa: E402
from zoneinfo import ZoneInfo

import pytest  # noqa: E402

JST = ZoneInfo("Asia/Tokyo")

import pytest  # noqa: E402

from util import api_base  # noqa: E402
from util.util import timestamp_fromdatetime  # noqa: E402


def get_date_time1(base_datetime, format: str = "%Y/%m/%d %H:%M:%S") -> str:
    date_time = datetime.fromtimestamp(int(base_datetime.timestamp()), tz=JST)
    date_time_str = date_time.strftime(format)
    return date_time_str


def get_date_time2(base_datetime, format: str = "%Y/%m/%d %H:%M:%S") -> str:
    date_time = datetime.fromtimestamp(int(base_datetime.timestamp()), tz=JST)
    # 朝08:59:59までを前日と見なすための基準時間を生成
    cutoff_time = datetime(
        date_time.year, date_time.month, date_time.day, 8, 59, 59, tzinfo=JST
    )
    # もし基準時間より前なら、日付を1日減らす
    if date_time <= cutoff_time:
        date_time -= timedelta(days=1)
    date_time_str = date_time.strftime(format)
    return date_time_str


def test_get_date_time():
    datetime1 = datetime(2023, 9, 15, 0, 0, 0, tzinfo=JST)
    datetime2 = datetime(2023, 9, 15, 23, 59, 59, tzinfo=JST)
    datetime3 = datetime(2023, 9, 16, 8, 59, 59, tzinfo=JST)

    print("get_date_time1")
    print(get_date_time1(datetime1))
    print(get_date_time1(datetime2))
    print(get_date_time1(datetime3))

    print("get_date_time2")
    print(get_date_time2(datetime1))
    print(get_date_time2(datetime2))
    print(get_date_time2(datetime3))


def test_unixtimestamp():
    start = datetime(2019, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)

    print(start.strftime("%Y-%m-%d %H:%M:%S"))
    print(end.strftime("%Y-%m-%d %H:%M:%S"))
