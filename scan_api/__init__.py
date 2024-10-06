import csv  # noqa: E402
import os
from datetime import datetime
from decimal import Decimal  # noqa: E402
from typing import (  # noqa: E402
    Dict,
    List,
    Literal,
    MutableSet,
    NotRequired,
    TypedDict,
    TypeGuard,
)

from util import api_base  # noqa: E402
from util.logger import get_logger

from . import blockscout, etherscan
from .types import SCAN_MAPPING, TYPE_SCANNAME, BlockScout, EtherScan, Scan
from .util import is_blockscout, is_etherscan, wei_to_token, write_csv

logger = get_logger()


def get_txlist(
    scan: Scan,
    address: str,
    start_datetime: datetime,
    end_datetime: datetime,
    output_directory: str = "./output",
):
    if is_etherscan(scan):
        return etherscan.get_etherscan_txlist(
            scan, address, start_datetime, end_datetime, output_directory
        )
    elif is_blockscout(scan):
        return blockscout.get_blockscout_txlist(
            scan, address, start_datetime, end_datetime, output_directory
        )
    else:
        raise ValueError(f"Unsupported scan type: {type(scan)}")


def get_txlist_internal(
    scan: Scan,
    address: str,
    start_datetime: datetime,
    end_datetime: datetime,
    output_directory: str = "./output",
):
    if is_etherscan(scan):
        return etherscan.get_etherscan_txlist_internal(
            scan, address, start_datetime, end_datetime, output_directory
        )
    elif is_blockscout(scan):
        return blockscout.get_blockscout_txlist_internal(
            scan, address, start_datetime, end_datetime, output_directory
        )
    else:
        raise ValueError(f"Unsupported scan type: {type(scan)}")


def get_txlist_token(
    scan: Scan,
    address: str,
    start_datetime: datetime,
    end_datetime: datetime,
    output_directory: str = "./output",
):
    if is_etherscan(scan):
        return etherscan.get_etherscan_txlist_token(
            scan, address, start_datetime, end_datetime, output_directory
        )
    elif is_blockscout(scan):
        return blockscout.get_blockscout_txlist_token(
            scan, address, start_datetime, end_datetime, output_directory
        )
    else:
        raise ValueError(f"Unsupported scan type: {type(scan)}")


def get_txlist_tokennft(
    scan: Scan,
    address: str,
    start_datetime: datetime,
    end_datetime: datetime,
    output_directory: str = "./output",
):
    if is_etherscan(scan):
        return etherscan.get_etherscan_txlist_tokennft(
            scan, address, start_datetime, end_datetime, output_directory
        )
    elif is_blockscout(scan):
        return blockscout.get_blockscout_txlist_tokennft(
            scan, address, start_datetime, end_datetime, output_directory
        )
    else:
        raise ValueError(f"Unsupported scan type: {type(scan)}")


def get_txlist_token1155(
    scan: Scan,
    address: str,
    start_datetime: datetime,
    end_datetime: datetime,
    output_directory: str = "./output",
):
    if is_etherscan(scan):
        return etherscan.get_etherscan_txlist_token1155(
            scan, address, start_datetime, end_datetime, output_directory
        )
    elif is_blockscout(scan):
        return blockscout.get_blockscout_txlist_token1155(
            scan, address, start_datetime, end_datetime, output_directory
        )
    else:
        raise ValueError(f"Unsupported scan type: {type(scan)}")
