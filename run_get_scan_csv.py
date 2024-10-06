from datetime import datetime  # noqa: E402
from zoneinfo import ZoneInfo

from scan_api import (
    SCAN_MAPPING,
    get_txlist,
    get_txlist_internal,
    get_txlist_token,
    get_txlist_token1155,
    get_txlist_tokennft,
)
from util.logger import setup_logger

setup_logger()

output_directory = "./output"

# scans = [SCAN_MAPPING["ethereum"]]
# address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
scans = [SCAN_MAPPING["defiverse"]]
address = "0x2FA699664752B34E90A414A42D62D7A8b2702B85"
# 日付指定したい場合defiverseは2024/8/25くらいから問い合わせ可能
# Noneにすればもっと以前から取得可能
start_jst = datetime(2024, 8, 25, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
end_jst = datetime(2024, 10, 1, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
# start_jst = None
# end_jst = None

for scan in scans:
    get_txlist(scan, address, start_jst, end_jst, output_directory)
    get_txlist_internal(scan, address, start_jst, end_jst, output_directory)
    get_txlist_token(scan, address, start_jst, end_jst, output_directory)
    get_txlist_tokennft(scan, address, start_jst, end_jst, output_directory)
    if scan.has_erc1155:
        get_txlist_token1155(scan, address, start_jst, end_jst, output_directory)
