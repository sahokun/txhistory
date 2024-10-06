from typing import (  # noqa: E402
    Dict,
    List,
    Literal,
    MutableSet,
    NotRequired,
    TypedDict,
    TypeGuard,
)

TYPE_SCANNAME = Literal[
    "ethereum",
    "polygon",
    "arbitrum",
    "optimism",
    "avalanche",
    "bsc",
    "oasys",
    "mchverse",
]
TYPE_ACTION = Literal[
    "txlist", "txlistinternal", "tokentx", "tokennfttx", "token1155tx"
]


class Scan:
    def __init__(
        self,
        name: str,
        network: str,
        url: str,
        key: str,
        token: str,
        decimals: int,
        has_erc1155: bool = False,
    ):
        self.name = name
        self.network = network
        self.url = url
        self.key = key
        self.token = token
        self.decimals = decimals
        self.has_erc1155 = has_erc1155


class EtherScan(Scan):
    pass


class BlockScout(Scan):
    def __init__(
        self,
        name: str,
        network: str,
        url: str,
        key: str,
        token: str,
        decimals: int,
        api_version: int,
        has_erc1155: bool = False,
    ):
        super().__init__(name, network, url, key, token, decimals, has_erc1155)
        self.api_version = api_version


SCAN_MAPPING: Dict[TYPE_SCANNAME, Scan] = {
    "ethereum": EtherScan(
        name="etherscan",
        network="ethereum",
        url="https://api.etherscan.io/api",
        key="",
        token="ETH",
        decimals=18,
    ),
    "polygon": EtherScan(
        name="polygonscan",
        network="polygon",
        url="https://api.polygonscan.com/api",
        key="",
        token="MATIC",
        decimals=18,
    ),
    "optimism": EtherScan(
        name="optimism etherscan",
        network="optimism",
        url="https://api-optimistic.etherscan.io/api",
        key="",
        token="ETH",
        decimals=18,
    ),
    "arbitrum": EtherScan(
        name="arbiscan",
        network="arbitrum",
        url="https://api.arbiscan.io/api",
        key="",
        token="ETH",
        decimals=18,
    ),
    "avalanche": EtherScan(
        name="snowtrace",
        network="avalanche",
        url="https://api.snowtrace.io/api",
        key="",
        token="ETH",
        decimals=18,
        has_erc1155=True,
    ),
    "bsc": EtherScan(
        name="bscscan",
        network="bsc",
        url="https://api.bscscan.com/api",
        key="",
        token="BNB",
        decimals=18,
    ),
    "oasys": BlockScout(
        name="oasys blockscout",
        network="oasys",
        url="https://explorer.oasys.games/api",
        key="",
        token="OAS",
        decimals=18,
        api_version=2,
    ),
    "mchverse": BlockScout(
        name="mch verse blockscout",
        network="mchverse",
        url="https://explorer.oasys.mycryptoheroes.net/api",
        key="",
        token="OAS",
        decimals=18,
        api_version=1,
    ),
    "zksync2": BlockScout(
        name="zksync era blockscout",
        network="zksync2",
        url="https://zksync.blockscout.com/api",
        key="",
        token="ETH",
        decimals=18,
        api_version=2,
    ),
    "scroll": EtherScan(
        name="scrollscan",
        network="scroll",
        url="https://api.scrollscan.com/api",
        key="",
        token="ETH",
        decimals=18,
        has_erc1155=False,
    ),
    "defiverse": BlockScout(
        name="defi verse blockscout",
        network="defiverse",
        url="https://scan.defi-verse.org/api",
        key="",
        token="OAS",
        decimals=18,
        api_version=2,
    ),
}
