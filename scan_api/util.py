import csv  # noqa: E402
import os
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

from util.logger import get_logger

from .types import BlockScout, EtherScan, Scan

logger = get_logger()


def wei_to_token(wei, decimals):
    return Decimal(wei) / Decimal(10**decimals)


def write_csv(
    directory: str,
    filename: str,
    field_names: List[str],
    data: List[dict],
    ignore_list: List[str] = [],
):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = "/".join([directory, filename])
    logger.info(file_path)
    with open(file_path, "w", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=field_names, strict=True, quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        for row in data:
            for ignore in ignore_list:
                row.pop(ignore, None)
            writer.writerow(row)


def is_etherscan(scan: Scan) -> TypeGuard[EtherScan]:
    return isinstance(scan, EtherScan)


def is_blockscout(scan: Scan) -> TypeGuard[BlockScout]:
    return isinstance(scan, BlockScout)
