from datetime import datetime  # noqa: E402

import pytest  # noqa: E402

from scan_api import SCAN_MAPPING
from scan_api.blockscout import (
    GetBlocknoBlockScoutApi,
    GetTxlistBlockScoutApi,
    get_blockscout_txlist,
    get_blockscout_txlist_internal,
    get_blockscout_txlist_token,
    get_blockscout_txlist_token1155,
    get_blockscout_txlist_tokennft,
)
from scan_api.etherscan import (
    GetBlocknoEtherscanApi,
    GetTxlistEtherscanApi,
    get_etherscan_txlist,
    get_etherscan_txlist_internal,
    get_etherscan_txlist_token,
    get_etherscan_txlist_token1155,
    get_etherscan_txlist_tokennft,
)


def test_output_blockno():
    scan = SCAN_MAPPING["ethereum"]
    start = datetime(2019, 1, 1, 0, 0, 0)
    end = datetime(2023, 10, 1, 0, 0, 0)
    get_blockno_api = GetBlocknoEtherscanApi(scan)
    startblockno = get_blockno_api.execute(timestamp=start)
    endblockno = get_blockno_api.execute(timestamp=end)
    print(startblockno)
    print(endblockno)
    assert True


def test_get_ethereum_txlist():
    scan = SCAN_MAPPING["ethereum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2022, 1, 1, 0, 0, 0)
    end = datetime(2023, 1, 1, 0, 0, 0)
    assert get_etherscan_txlist(scan, address, start, end)


def test_get_ethereum_txlist_internal():
    scan = SCAN_MAPPING["ethereum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_internal(scan, address, start, end)


def test_get_ethereum_txlist_token():
    scan = SCAN_MAPPING["ethereum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token(scan, address, start, end)


def test_get_ethereum_txlist_tokennft():
    scan = SCAN_MAPPING["ethereum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_tokennft(scan, address, start, end)


def test_get_ethereum_txlist_token1155():
    scan = SCAN_MAPPING["ethereum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token1155(scan, address, start, end)


def test_get_polygon_txlist():
    scan = SCAN_MAPPING["polygon"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist(scan, address, start, end)


def test_get_polygon_txlist_internal():
    scan = SCAN_MAPPING["polygon"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_internal(scan, address, start, end)


def test_get_polygon_txlist_token():
    scan = SCAN_MAPPING["polygon"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token(scan, address, start, end)


def test_get_polygon_txlist_tokennft():
    scan = SCAN_MAPPING["polygon"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_tokennft(scan, address, start, end)


def test_get_polygon_txlist_token1155():
    scan = SCAN_MAPPING["polygon"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token1155(scan, address, start, end)


def test_get_optimism_txlist():
    scan = SCAN_MAPPING["optimism"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist(scan, address, start, end)


def test_get_optimism_txlist_internal():
    scan = SCAN_MAPPING["optimism"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_internal(scan, address, start, end)


def test_get_optimism_txlist_token():
    scan = SCAN_MAPPING["optimism"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token(scan, address, start, end)


def test_get_optimism_txlist_tokennft():
    scan = SCAN_MAPPING["optimism"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_tokennft(scan, address, start, end)


def test_get_optimism_txlist_token1155_x():
    # 1155取得API存在しない
    scan = SCAN_MAPPING["optimism"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token1155(scan, address, start, end)


def test_get_arbitrum_txlist():
    scan = SCAN_MAPPING["arbitrum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist(scan, address, start, end)


def test_get_arbitrum_txlist_internal():
    scan = SCAN_MAPPING["arbitrum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    get_etherscan_txlist_internal(scan, address, start, end)
    assert True


def test_get_arbitrum_txlist_token():
    scan = SCAN_MAPPING["arbitrum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    get_etherscan_txlist_token(scan, address, start, end)
    assert True


def test_get_arbitrum_txlist_tokennft():
    scan = SCAN_MAPPING["arbitrum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_tokennft(scan, address, start, end)


def test_get_arbitrum_txlist_token1155_x():
    # 1155取得API存在しない
    scan = SCAN_MAPPING["arbitrum"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token1155(scan, address, start, end)


def test_get_avalanche_txlist():
    scan = SCAN_MAPPING["avalanche"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist(scan, address, start, end)


def test_get_avalanche_txlist_internal():
    scan = SCAN_MAPPING["avalanche"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_internal(scan, address, start, end)


def test_get_avalanche_txlist_token():
    scan = SCAN_MAPPING["avalanche"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token(scan, address, start, end)


def test_get_avalanche_txlist_tokennft():
    scan = SCAN_MAPPING["avalanche"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_tokennft(scan, address, start, end)


def test_get_avalanche_txlist_token1155():
    scan = SCAN_MAPPING["avalanche"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token1155(scan, address, start, end)


def test_get_bsc_txlist():
    scan = SCAN_MAPPING["bsc"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2021, 1, 1, 0, 0, 0)
    end = datetime(2021, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist(scan, address, start, end)


def test_get_bsc_txlist_internal():
    scan = SCAN_MAPPING["bsc"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2021, 1, 1, 0, 0, 0)
    end = datetime(2021, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_internal(scan, address, start, end)


def test_get_bsc_txlist_token():
    scan = SCAN_MAPPING["bsc"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2021, 1, 1, 0, 0, 0)
    end = datetime(2021, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token(scan, address, start, end)


def test_get_bsc_txlist_tokennft():
    scan = SCAN_MAPPING["bsc"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2021, 1, 1, 0, 0, 0)
    end = datetime(2021, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_tokennft(scan, address, start, end)


def test_get_bsc_txlist_token1155_x():
    # 1155取得API存在しない
    scan = SCAN_MAPPING["bsc"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2021, 1, 1, 0, 0, 0)
    end = datetime(2021, 9, 30, 23, 59, 59)
    assert get_etherscan_txlist_token1155(scan, address, start, end)


def test_get_oasys_txlist():
    scan = SCAN_MAPPING["oasys"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist(scan, address, start, end)


def test_get_oasys_txlist_internal():
    scan = SCAN_MAPPING["oasys"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_internal(scan, address, start, end)


def test_get_oasys_txlist_token():
    scan = SCAN_MAPPING["oasys"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_token(scan, address, start, end)


def test_get_oasys_txlist_tokennft():
    scan = SCAN_MAPPING["oasys"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_tokennft(scan, address, start, end)


def test_get_oasys_txlist_token1155():
    scan = SCAN_MAPPING["oasys"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_token1155(scan, address, start, end)


def test_get_mchverse_txlist():
    scan = SCAN_MAPPING["mchverse"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist(scan, address, start, end)


def test_get_mchverse_txlist_internal():
    scan = SCAN_MAPPING["mchverse"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_internal(scan, address, start, end)


def test_get_mchverse_txlist_token():
    scan = SCAN_MAPPING["mchverse"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_token(scan, address, start, end)


def test_get_mchverse_txlist_tokennft():
    scan = SCAN_MAPPING["mchverse"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_tokennft(scan, address, start, end)


def test_get_mchverse_txlist_token1155():
    scan = SCAN_MAPPING["mchverse"]
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_token1155(scan, address, start, end)


def test_get_defiverse_txlist():
    scan = SCAN_MAPPING["defiverse"]
    address = "0x2FA699664752B34E90A414A42D62D7A8b2702B85"
    start = datetime(2024, 9, 1, 0, 0, 0)
    end = datetime(2024, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist(scan, address, start, end)


def test_get_defiverse_txlist_internal():
    scan = SCAN_MAPPING["defiverse"]
    address = "0x2FA699664752B34E90A414A42D62D7A8b2702B85"
    start = datetime(2024, 9, 1, 0, 0, 0)
    end = datetime(2024, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_internal(scan, address, start, end)


def test_get_defiverse_txlist_token():
    scan = SCAN_MAPPING["defiverse"]
    address = "0x2FA699664752B34E90A414A42D62D7A8b2702B85"
    start = datetime(2024, 9, 1, 0, 0, 0)
    end = datetime(2024, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_token(scan, address, start, end)


def test_get_defiverse_txlist_tokennft():
    scan = SCAN_MAPPING["defiverse"]
    address = "0x2FA699664752B34E90A414A42D62D7A8b2702B85"
    start = datetime(2024, 9, 1, 0, 0, 0)
    end = datetime(2024, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_tokennft(scan, address, start, end)


def test_get_defiverse_txlist_token1155():
    scan = SCAN_MAPPING["defiverse"]
    address = "0x2FA699664752B34E90A414A42D62D7A8b2702B85"
    start = datetime(2024, 9, 1, 0, 0, 0)
    end = datetime(2024, 9, 30, 23, 59, 59)
    assert get_blockscout_txlist_token1155(scan, address, start, end)
