import abc
import copy
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from itertools import islice
from sys import stdout
from typing import List, Set, TypedDict, TypeGuard
from zoneinfo import ZoneInfo

import pandas as pd

from util.util import get_rate, to_decimal
from wopenpyxl import WOpenpyxl

JST = ZoneInfo("Asia/Tokyo")

Network = TypedDict("Network", {"name": str, "symbol": str})
SymbolMap = TypedDict(
    "SymbolMap", {"from_contract": str, "from_name": str, "to_symbol": str}
)

TransationFileMap = TypedDict(
    "TransationFileMap", {"class": List[type], "file_name": str}
)

SYMBOL_MAPPING: List[SymbolMap] = []

NETWORKS: List[Network] = [
    {"name": "bitcoin", "symbol": "BTC"},
    {"name": "ethereum", "symbol": "ETH"},
    {"name": "polygon", "symbol": "MATIC"},
    {"name": "zkevm", "symbol": "ETH"},
    {"name": "optimism", "symbol": "ETH"},
    {"name": "arbitrum", "symbol": "ETH"},
    {"name": "oasys", "symbol": "OAS"},
    {"name": "mchverse", "symbol": "OAS"},
    {"name": "zksync1", "symbol": "ETH"},
    {"name": "zksync2", "symbol": "ETH"},
    {"name": "base", "symbol": "ETH"},
    {"name": "scroll", "symbol": "ETH"},
    {"name": "avalanche", "symbol": "AVAX"},
    {"name": "bsc", "symbol": "BNB"},
    {"name": "solana", "symbol": "SOL"},
    {"name": "fantom", "symbol": "FTM"},
    {"name": "defiverse", "symbol": "OAS"},
]

BASE_SYMBOLS = ["OAS"]


def load_rate_df():
    book = WOpenpyxl("./data/rate.xlsx", data_only=True)
    data = book.active_sheet.values
    cols = next(data)[1:]
    data = list(data)
    data = (islice(r, 1, None) for r in data)
    df = pd.DataFrame(data, columns=cols)
    return df


rate_df = load_rate_df()


class TradeAttribute(Enum):
    EXECUTE = 1
    INCOME = 2
    OUTCOME = 3
    IN_NFT = 4
    OUT_NFT = 5
    CREATE = 6
    SELF = 7


class AnalyzeCsvError(Exception):
    """"""


class OutputRecord:
    def __init__(
        self,
        network: str,
        my_address: str,
        txhash,
        date_time,
        method,
        counterparty,
        counterparty_name,
        trade,
        application,
        status,
        manual_selling_price,
        manual_selling_cost,
        manual_currency_rate,
        quantity,
        currency,
        currency_rate,
        fiat_quantity,
        fiat_currency,
        fee_quantity,
        fee_currency,
        fee_currency_rate,
        fee_fiat_quantity,
        fee_fiat_currency,
        dallar_yen,
        result_selling_price,
        result_selling_cost,
        result_fee_fiat_quantity,
        private_note,
    ):
        self.network = network
        self.my_address = my_address
        self.txhash = txhash
        self.date_time = date_time
        self.method = method
        self.counterparty = counterparty
        self.counterparty_name = counterparty_name
        self.trade = trade  # 実行/転入/スワップ/NFT売却/転送/ボーナス
        self.application = application  # メモ
        self.status = status
        self.manual_selling_price = manual_selling_price
        self.manual_selling_cost = manual_selling_cost
        self.manual_currency_rate = manual_currency_rate
        self.quantity = quantity
        self.currency = currency
        self.currency_rate = currency_rate
        self.fiat_quantity = fiat_quantity
        self.fiat_currency = fiat_currency
        self.fee_quantity = fee_quantity
        self.fee_currency = fee_currency
        self.fee_currency_rate = fee_currency_rate
        self.fee_fiat_quantity = fee_fiat_quantity
        self.fee_fiat_currency = fee_fiat_currency
        self.dallar_yen = dallar_yen
        self.result_selling_price = result_selling_price
        self.result_selling_cost = result_selling_cost
        self.result_fee_fiat_quantity = result_fee_fiat_quantity
        self.private_note = private_note
        self.validate()

    def validate(self):
        pass

    def to_csv_row(self):
        output = list(
            (
                self.network,
                self.my_address,
                self.txhash,
                self.date_time,
                self.method,
                self.counterparty,
                self.counterparty_name,
                self.trade,
                self.application,
                self.status,
                self.manual_selling_price,
                self.manual_selling_cost,
                self.manual_currency_rate,
                self.quantity,
                self.currency,
                self.currency_rate,
                self.fiat_quantity,
                self.fiat_currency,
                self.fee_quantity,
                self.fee_currency,
                self.fee_currency_rate,
                self.fee_fiat_quantity,
                self.fee_fiat_currency,
                self.dallar_yen,
                self.result_selling_price,
                self.result_selling_cost,
                self.result_fee_fiat_quantity,
                self.private_note,
            )
        )
        return output


class AbstractRecord(metaclass=abc.ABCMeta):
    def __init__(self, network: Network, my_address: str, name: str, header, record):
        self.is_skip = False

        self.network = network
        self.my_address = my_address.lower()
        self.name = name

    def get_date_time(self, format: str = "%Y/%m/%d %H:%M:%S") -> str:
        date_time = datetime.fromtimestamp(int(self.unix_timestamp), tz=JST)
        date_time_str = date_time.strftime(format)
        return date_time_str

    def get_trading_date(self) -> str:
        format: str = "%Y/%m/%d"
        date_time = datetime.fromtimestamp(int(self.unix_timestamp), tz=JST)
        # 朝08:59:59までを前日と見なすための基準時間を生成
        cutoff_time = datetime(
            date_time.year, date_time.month, date_time.day, 8, 59, 59, tzinfo=JST
        )
        # もし基準時間より前なら、日付を1日減らす
        if date_time <= cutoff_time:
            date_time -= timedelta(days=1)
        date_time_str = date_time.strftime(format)
        return date_time_str

    def get_counterparty(self):
        counterparty = (
            self.txn_to if self.txn_from == self.my_address else self.txn_from
        )
        counterparty = counterparty if counterparty != "" else self.contract_address
        return counterparty

    def __repr__(self):
        #: Columns.
        user_dict = dict(
            filter(lambda item: item[0] != "password", self.__dict__.items())
        )
        columns = ", ".join(
            [
                "{0}={1}".format(k, repr(user_dict[k]))
                for k in user_dict.keys()
                if k[0] != "_"
            ]
        )

        return "<{0}({1})>".format(self.__class__.__name__, columns)


class TransactionRecord(AbstractRecord):
    status_white_list = ["", "error(0)", "error(1)"]
    err_code_white_list = [
        "",
        "!unknown!",
        "revert",
        "reverted",
        "out of gas",
        "execution reverted",
        "invalid opcode: opcode 0xa9 not defined",
    ]

    def __init__(self, network: Network, my_address: str, name: str, header, record):
        super().__init__(network, my_address, name, header, record)

        record = copy.copy(record)
        self.analyze_header(header)

        self.txhash = record.pop(0)
        self.blockno = record.pop(0)
        self.unix_timestamp = record.pop(0)
        self.date_time = record.pop(0)
        self.txn_from = record.pop(0).lower()
        if self.has_private_tag:
            # from private tag
            record.pop(0)
        self.txn_to = record.pop(0).lower()
        if self.has_private_tag:
            # from private tag
            record.pop(0)
        self.contract_address = record.pop(0).lower()
        self.value_in_eth = to_decimal(record.pop(0))
        self.value_out_eth = to_decimal(record.pop(0))
        self.current_value_eth = record.pop(0)
        self.txn_fee_eth = to_decimal(record.pop(0))
        self.txn_fee_usd = record.pop(0)
        self.historical_price_eth = record.pop(0)
        self.status = record.pop(0)
        self.err_code = record.pop(0)
        self.method = record.pop(0)
        self.private_note = record.pop(0) if len(record) > 0 else ""

        self.calc()

    def analyze_header(self, header):
        self.has_private_tag = True if "From_PrivateTag" in header else False

    def validate(self):
        if self.value_in_eth != 0 and self.value_out_eth != 0:
            raise ValueError("value in ethとvalue out ethは排他")
        if (
            self.txn_from != self.my_address
            and self.txn_to != self.my_address
            and TradeAttribute.CREATE not in self.attributes
        ):
            # CREATEの場合はfrom他アドレス、to空、contract_addressが自分となる
            raise ValueError("from/toどちらも自分ではない")
        if self.txn_from == "" and self.txn_to == "" and self.contract_address == "":
            raise ValueError("取引相手不明")
        if self.status.lower() not in TransactionRecord.status_white_list:
            raise ValueError("未知のSTATUS", self.status.lower())
        if self.err_code.lower() not in TransactionRecord.err_code_white_list:
            raise ValueError("未知のERRCODE", self.err_code)

    def evalute_attribute(self):
        self.attributes.append(TradeAttribute.EXECUTE)
        if self.value_in_eth != 0:
            self.attributes.append(TradeAttribute.INCOME)
        if self.value_out_eth != 0:
            self.attributes.append(TradeAttribute.OUTCOME)

        if self.txn_to == "" and self.contract_address == self.my_address:
            self.attributes.append(TradeAttribute.CREATE)

    def calc(self):
        self.attributes: List[TradeAttribute] = list()
        self.evalute_attribute()

        self.trade = ""
        self.counterparty = self.get_counterparty()
        self.unit_price = get_rate(
            self.network["symbol"], self.get_trading_date(), rate_df
        )

        # 通常In/Outは排他
        # ブリッジ/自己送金の時は両方に同じ値が入る
        # ブリッジの場合は更にgasfeeが0
        if (
            self.value_in_eth > 0
            and self.value_out_eth > 0
            and (self.value_in_eth == self.value_out_eth)
        ):
            if self.txn_fee_eth == 0:
                # ブリッジ、outを0にして残高を増やす
                self.value_out_eth = 0
            else:
                # 自己送金、IN/OUTを相殺する
                self.value_in_eth = 0
                self.value_out_eth = 0

        self.quantity = self.get_quantity()
        self.fiat_quantity = (
            self.unit_price * self.quantity if self.unit_price != "N/A" else "N/A"
        )

        self.validate()

    def get_quantity(self) -> Decimal:
        quantity = (
            self.value_in_eth if self.value_in_eth != 0 else -1 * self.value_out_eth
        )
        return quantity

    def get_fee_quantity(self) -> Decimal:
        fee_quantity = self.txn_fee_eth if self.txn_from == self.my_address else 0
        return fee_quantity

    def get_status(self) -> str:
        status = self.err_code if self.status.lower() == "error(0)" else ""
        return status


class InternalTxnRecord(AbstractRecord):
    status_white_list = ["", "0"]
    err_code_white_list = [""]

    def __init__(self, network: Network, my_address: str, name: str, header, record):
        super().__init__(network, my_address, name, header, record)

        record = copy.copy(record)
        self.analyze_header(header)

        self.txhash = record.pop(0)
        self.blockno = record.pop(0)
        self.unix_timestamp = record.pop(0)
        self.date_time = record.pop(0)
        self.parent_txn_from = record.pop(0).lower()
        if self.has_private_tag:
            # from private tag
            record.pop(0)
        self.parent_txn_to = record.pop(0).lower()
        if self.has_private_tag:
            # from private tag
            record.pop(0)
        self.parent_txn_eth_value = record.pop(0)  # 無視の予定
        self.txn_from = record.pop(0)
        if self.has_private_tag:
            # from private tag
            record.pop(0)
        self.txn_to = record.pop(0)
        if self.has_private_tag:
            # from private tag
            record.pop(0)
        self.contract_address = record.pop(0).lower()
        self.value_in_eth = to_decimal(record.pop(0))
        self.value_out_eth = to_decimal(record.pop(0))
        self.current_value_eth = record.pop(0)
        self.historical_price_eth = record.pop(0)
        self.status = record.pop(0)
        self.err_code = record.pop(0)
        self.type = record.pop(0)
        self.private_note = record.pop(0) if len(record) > 0 else ""

        self.calc()

    def analyze_header(self, header):
        self.has_private_tag = True if "ParentTxFrom_PrivateTag" in header else False

    def validate(self):
        if self.txn_from == self.my_address and self.txn_to == self.my_address:
            raise ValueError("from/toどちらも自分かつ送金あり(未実装)")
        if (
            self.txn_from != self.my_address
            and self.txn_to != self.my_address
            and self.contract_address != self.my_address
        ):
            # contractウォレットの場合を考慮してcontractとも比較
            raise ValueError("from/toどちらも自分ではない")
        if self.status.lower() not in InternalTxnRecord.status_white_list:
            raise ValueError("未知のSTATUS")
        if self.err_code.lower() not in InternalTxnRecord.err_code_white_list:
            raise ValueError("未知のERRCODE")

    def evalute_attribute(self):
        if self.type == "create":
            self.attributes.append(TradeAttribute.CREATE)
        if self.value_in_eth != 0:
            self.attributes.append(TradeAttribute.INCOME)
        if self.value_out_eth != 0:
            self.attributes.append(TradeAttribute.OUTCOME)

    def calc(self):
        self.attributes: List[TradeAttribute] = list()
        self.evalute_attribute()

        self.trade = ""
        self.counterparty = self.get_counterparty()
        self.unit_price = get_rate(
            self.network["symbol"], self.get_trading_date(), rate_df
        )
        self.quantity = self.get_quantity()
        self.fiat_quantity = (
            self.unit_price * self.quantity if self.unit_price != "N/A" else "N/A"
        )

        self.validate()

    def get_quantity(self) -> Decimal:
        quantity = self.value_in_eth if self.value_in_eth != 0 else self.value_out_eth
        return quantity

    def get_status(self) -> str:
        status = self.err_code if self.status.lower() != "0" else ""
        return status


class Erc20TxnRecord(AbstractRecord):
    def __init__(self, network: Network, my_address: str, name: str, header, record):
        super().__init__(network, my_address, name, header, record)

        record = copy.copy(record)
        self.analyze_header(header)

        self.txhash = record.pop(0)
        self.blockno = record.pop(0) if self.has_blockno else ""
        self.unix_timestamp = record.pop(0)
        self.date_time = record.pop(0)
        self.txn_from = record.pop(0).lower()
        if self.has_private_tag:
            # from private tag
            record.pop(0)
        self.txn_to = record.pop(0).lower()
        if self.has_private_tag:
            # from private tag
            record.pop(0)
        self.value = to_decimal(record.pop(0))
        self.historical_value_usd = record.pop(0)
        self.contract_address = record.pop(0).lower()
        self.token_name = record.pop(0)
        self.token_symbol = self.get_fixed_symbol(record.pop(0))
        self.private_note = record.pop(0) if len(record) > 0 else ""

        self.adjustment_unit_price = ""

        # zksync2のガス代のやりとりは不要なのでスキップ
        if self.network["name"] == "zksync2" and (
            self.txn_from == "0x0000000000000000000000000000000000008001"
            or self.txn_to == "0x0000000000000000000000000000000000008001"
        ):
            self.is_skip = True
            return

        self.calc()

    def analyze_header(self, header):
        self.has_private_tag = True if "From_PrivateTag" in header else False
        self.has_blockno = True if "Blockno" in header else False

    def validate(self):
        pass
        # scamで結構あるのでtrade判定の方に移動
        # if self.txn_from != self.my_address and self.txn_to != self.my_address:
        #     raise ValueError("from/toどちらも自分ではない")

    def evalute_attribute(self):
        if self.txn_to == self.my_address:
            self.attributes.append(TradeAttribute.INCOME)
        if self.txn_from == self.my_address:
            self.attributes.append(TradeAttribute.OUTCOME)
        if self.txn_from == "self" or self.txn_to == "self":
            self.attributes.append(TradeAttribute.SELF)

    def calc(self):
        self.attributes: List[TradeAttribute] = list()
        self.evalute_attribute()
        self.trade = ""
        self.counterparty = self.get_counterparty()
        self.unit_price = get_rate(self.token_symbol, self.get_trading_date(), rate_df)
        self.quantity = self.get_quantity()
        self.fiat_quantity = (
            self.unit_price * self.quantity if self.unit_price != "N/A" else ""
        )

        self.validate()

    def get_quantity(self) -> Decimal:
        quantity = self.value
        if self.txn_from == self.my_address:
            quantity = quantity * -1

        return quantity

    def get_fixed_symbol(self, symbol) -> str:
        value = symbol
        search_result = next(
            filter(
                lambda mapping: mapping["from_contract"] == self.contract_address
                and mapping["from_name"] == self.token_name,
                SYMBOL_MAPPING,
            ),
            None,
        )
        if search_result:
            value = search_result["to_symbol"]

        return value


class Erc721TxnRecord(AbstractRecord):
    def __init__(self, network: Network, my_address: str, name: str, header, record):
        super().__init__(network, my_address, name, header, record)

        record = copy.copy(record)
        self.analyze_header(header)

        self.is_erc721 = (
            True
            if not self.is_new_format or record[header.index("Type")] == "721"
            else False
        )

        if not self.is_erc721:
            self.is_skip = True
            return
        if self.is_new_format:
            self.txhash = record.pop(0)
            self.blockno = record.pop(0) if self.has_blockno else ""
            self.unix_timestamp = record.pop(0)
            self.date_time = record.pop(0)
            self.txn_from = record.pop(0).lower()
            if self.has_private_tag:
                # from private tag
                record.pop(0)
            self.txn_to = record.pop(0).lower()
            if self.has_private_tag:
                # from private tag
                record.pop(0)
            self.contract_address = record.pop(0).lower()
            self.token_name = record.pop(0)
            self.token_symbol = record.pop(0)
            self.token_id = record.pop(0)
            record.pop(0)  # Type
            self.quantity = int(record.pop(0))
            self.private_note = record.pop(0) if len(record) > 0 else ""

        else:
            self.txhash = record.pop(0)
            self.blockno = record.pop(0) if self.has_blockno else ""
            self.unix_timestamp = record.pop(0)
            self.date_time = record.pop(0)
            self.txn_from = record.pop(0).lower()
            if self.has_private_tag:
                # from private tag
                record.pop(0)
            self.txn_to = record.pop(0).lower()
            if self.has_private_tag:
                # from private tag
                record.pop(0)
            self.contract_address = record.pop(0).lower()
            self.token_id = record.pop(0)
            self.token_name = record.pop(0)
            self.token_symbol = record.pop(0)
            self.quantity = 1
            self.private_note = record.pop(0) if len(record) > 0 else ""

        self.calc()

    def analyze_header(self, header):
        self.is_new_format = True if "Type" in header else False
        self.has_private_tag = True if "From_PrivateTag" in header else False
        self.has_blockno = True if "Blockno" in header else False

    def validate(self):
        pass
        # scamで結構あるのでtrade判定の方に移動
        # if self.txn_from != self.my_address and self.txn_to != self.my_address:
        #     raise ValueError("from/toどちらも自分ではない")

    def evalute_attribute(self):
        if self.my_address == self.txn_to:
            self.attributes.append(TradeAttribute.INCOME)
        if self.my_address == self.txn_from:
            self.attributes.append(TradeAttribute.OUTCOME)
        if self.txn_from == "self" or self.txn_to == "self":
            self.attributes.append(TradeAttribute.SELF)

    def calc(self):
        self.attributes: List[TradeAttribute] = list()
        self.evalute_attribute()

        self.trade = ""
        self.counterparty = self.get_counterparty()
        self.unit_price = ""

        self.validate()


class Erc1155TxnRecord(AbstractRecord):
    def __init__(self, network: Network, my_address: str, name: str, header, record):
        super().__init__(network, my_address, name, header, record)

        record = copy.copy(record)
        self.analyze_header(header)

        self.is_erc1155 = (
            True
            if not self.is_new_format or record[header.index("Type")] == "1155"
            else False
        )

        if not self.is_erc1155:
            self.is_skip = True
            return
        if self.is_new_format:
            self.txhash = record.pop(0)
            self.blockno = record.pop(0) if self.has_blockno else ""
            self.unix_timestamp = record.pop(0)
            self.date_time = record.pop(0)
            self.txn_from = record.pop(0).lower()
            if self.has_private_tag:
                # from private tag
                record.pop(0)
            self.txn_to = record.pop(0).lower()
            if self.has_private_tag:
                # from private tag
                record.pop(0)
            self.contract_address = record.pop(0).lower()
            self.token_name = record.pop(0)
            self.token_symbol = record.pop(0)
            self.token_id = record.pop(0)
            record.pop(0)  # Type
            self.quantity = int(record.pop(0))
            self.private_note = record.pop(0) if len(record) > 0 else ""
        else:
            self.txhash = record.pop(0)
            self.blockno = record.pop(0) if self.has_blockno else ""
            self.unix_timestamp = record.pop(0)
            self.date_time = record.pop(0)
            self.txn_from = record.pop(0).lower()
            if self.has_private_tag:
                # from private tag
                record.pop(0)
            self.txn_to = record.pop(0).lower()
            if self.has_private_tag:
                # from private tag
                record.pop(0)
            self.contract_address = record.pop(0).lower()
            self.token_id = record.pop(0)
            self.quantity = int(record.pop(0))
            self.token_name = record.pop(0)
            self.token_symbol = record.pop(0)
            self.private_note = record.pop(0) if len(record) > 0 else ""

        self.calc()

    def analyze_header(self, header):
        self.is_new_format = True if "Type" in header else False
        self.has_private_tag = True if "From_PrivateTag" in header else False
        self.has_blockno = True if "Blockno" in header else False

    def validate(self):
        pass
        # scamで結構あるのでtrade判定の方に移動
        # if self.txn_from != self.my_address and self.txn_to != self.my_address:
        #     raise ValueError("from/toどちらも自分ではない")

    def evalute_attribute(self):
        if self.my_address == self.txn_to:
            self.attributes.append(TradeAttribute.INCOME)
        if self.my_address == self.txn_from:
            self.attributes.append(TradeAttribute.OUTCOME)

    def calc(self):
        self.attributes: List[TradeAttribute] = list()
        self.evalute_attribute()

        self.trade = ""
        self.counterparty = self.get_counterparty()
        self.unit_price = ""

        self.validate()


def is_transaction_record(val: AbstractRecord) -> TypeGuard[TransactionRecord]:
    return isinstance(val, TransactionRecord)


def is_internal_txn_record(val: AbstractRecord) -> TypeGuard[InternalTxnRecord]:
    return isinstance(val, InternalTxnRecord)


def is_erc20_txn_record(val: AbstractRecord) -> TypeGuard[Erc20TxnRecord]:
    return isinstance(val, Erc20TxnRecord)


def is_erc721_txn_record(val: AbstractRecord) -> TypeGuard[Erc721TxnRecord]:
    return isinstance(val, Erc721TxnRecord)


def is_erc1155_txn_record(val: AbstractRecord) -> TypeGuard[Erc1155TxnRecord]:
    return isinstance(val, Erc1155TxnRecord)


class TransactionGroup:
    @classmethod
    def makeHeader(cls):
        return list(
            (
                "txhash",
                "date_time",
                "method",
                "counterparty",
                "counterparty_name",
                "trade",
                "application",
                "status",
                "quantity",
                "currency",
                "fiat_quantity",
                "fiat_currency",
                "fee_quantity",
                "fee_currency",
                "fee_fiat_quantity",
                "fee_fiat_currency",
                "dallar_yen",
                "売却価額",
                "売却原価",
                "手数料",
                "private_note",
            )
        )

    def __init__(self):
        self.attributes: List[TradeAttribute] = list()
        self.transaction_record: TransactionRecord = None
        self.internal_txn_records: List[InternalTxnRecord] = list()
        self.erc20_txn_records: List[Erc20TxnRecord] = list()
        self.erc721_txn_records: List[Erc721TxnRecord] = list()
        self.erc1155_txn_records: List[Erc1155TxnRecord] = list()
        self.network: Network = None
        self.my_address: str = ""
        self.txhash: str = ""
        self.unix_timestamp: str = ""
        self.date_time: str = ""
        self.method: str = ""
        self.status: str = ""
        self.private_note: str = ""

    def add_records(self, records: List[AbstractRecord]):
        for record in records:
            # debug
            # if (
            #    record.txhash
            #    == ""
            # ):
            #    print("stop")

            self.network: Network = record.network
            self.my_address = record.my_address
            if is_transaction_record(record):
                if self.transaction_record is not None:
                    raise Exception("double transaction")
                self.transaction_record = record
                self.txhash = record.txhash
                self.unix_timestamp = record.unix_timestamp
                self.date_time = record.get_date_time()
                self.method = record.method
                self.status = record.get_status()
                self.private_note = self.private_note + record.private_note
                self.add_attributes(record.attributes)
            elif is_internal_txn_record(record):
                self.internal_txn_records.append(record)
                self.txhash = record.txhash
                self.unix_timestamp = record.unix_timestamp
                self.date_time = record.get_date_time()
                self.status = record.get_status()
                self.private_note = self.private_note + record.private_note
                self.add_attributes(record.attributes)
            elif is_erc20_txn_record(record):
                self.erc20_txn_records.append(record)
                self.txhash = record.txhash
                self.unix_timestamp = record.unix_timestamp
                self.date_time = record.get_date_time()
                self.private_note = self.private_note + record.private_note
                self.add_attributes(record.attributes)
            elif is_erc721_txn_record(record):
                self.erc721_txn_records.append(record)
                self.txhash = record.txhash
                self.unix_timestamp = record.unix_timestamp
                self.date_time = record.get_date_time()
                self.application = f"{record.token_name}#{record.token_id}"
                self.private_note = self.private_note + record.private_note
                self.add_attributes(record.attributes)
            elif is_erc1155_txn_record(record):
                self.erc1155_txn_records.append(record)
                self.txhash = record.txhash
                self.unix_timestamp = record.unix_timestamp
                self.date_time = record.get_date_time()
                self.application = f"{record.token_name}#{record.token_id}"
                self.private_note = self.private_note + record.private_note
                self.add_attributes(record.attributes)
            else:
                raise Exception("unexpected record")

        self.add_records_plugin()

    def add_records_plugin(self):
        if self.network["name"] == "zksync2" and self.transaction_record:
            self.transaction_record.value_in_eth = 0
            self.transaction_record.value_out_eth = 0

        if len(self.erc20_txn_records) > 0:
            additionl_records: List[Erc20TxnRecord] = list()
            for record in self.erc20_txn_records:
                if (
                    record.txn_from == self.my_address
                    and record.txn_from == record.txn_to
                ):
                    # ERC20 自己送金は打ち消し
                    record_backup = copy.copy(record)
                    record.txn_to = "self"
                    record.calc()
                    csv_record = [
                        self.txhash,
                        self.unix_timestamp,
                        self.date_time,
                        "self",
                        record_backup.txn_to,
                        str(abs(record_backup.quantity)),
                        record_backup.historical_value_usd,
                        record_backup.contract_address,
                        record_backup.token_name,
                        record_backup.token_symbol,
                        record_backup.private_note,
                    ]
                    tx_record = Erc20TxnRecord(
                        self.network, self.my_address, record.name, [], csv_record
                    )
                    additionl_records.append(tx_record)
                    self.add_attributes(tx_record.attributes)
            self.erc20_txn_records.extend(additionl_records)

        wrapped_eth_address = [
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # ethereum
            "0x4200000000000000000000000000000000000006",  # optimism/base
            "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",  # arbitrum
            "0x4F9A0e7FD2Bf6067db6994CF12E4495Df938E6e9",  # zkevm
            "0x5aea5775959fbc2557cc8789bc1bf90a239d9a91",  # zksync2
        ]
        lowercase_wrapped_eth_address = [
            address.lower() for address in wrapped_eth_address
        ]
        if (
            self.transaction_record
            and self.transaction_record.txn_to in lowercase_wrapped_eth_address
        ):
            if self.transaction_record.method == "Deposit":
                # WETH Deposit
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_to,
                    self.transaction_record.txn_from,
                    str(abs(self.transaction_record.quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WETH",
                    "WETH",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

            elif (
                self.transaction_record.method == "Withdraw"
                # TODO ここ本当に必要か、必要なら他のW系には不要なのか
                and len(self.internal_txn_records) > 0
            ):
                # WETH Withdraw
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_from,
                    self.transaction_record.txn_to,
                    str(abs(self.internal_txn_records[0].quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WETH",
                    "WETH",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

        wrapped_matic_address = [
            "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  # polygon
        ]
        lowercase_wrapped_matic_address = [
            address.lower() for address in wrapped_matic_address
        ]
        if (
            self.transaction_record
            and self.transaction_record.txn_to in lowercase_wrapped_matic_address
        ):
            if self.transaction_record.method == "Deposit":
                # WMATIC Deposit
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_to,
                    self.transaction_record.txn_from,
                    str(abs(self.transaction_record.quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WMATIC",
                    "WMATIC",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

            elif (
                self.transaction_record.method == "Withdraw"
                # TODO ここ本当に必要か、必要なら他のW系には不要なのか
                and len(self.internal_txn_records) > 0
            ):
                # WMATIC Withdraw
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_from,
                    self.transaction_record.txn_to,
                    str(abs(self.internal_txn_records[0].quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WMATIC",
                    "WMATIC",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

        wrapped_bnb_address = [
            "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # bsc
        ]
        lowercase_wrapped_bnb_address = [
            address.lower() for address in wrapped_bnb_address
        ]
        if (
            self.transaction_record
            and self.transaction_record.txn_to in lowercase_wrapped_bnb_address
        ):
            if self.transaction_record.method == "Deposit":
                # WBNB Deposit
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_to,
                    self.transaction_record.txn_from,
                    str(abs(self.transaction_record.quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WBNB",
                    "WBNB",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

            elif (
                self.transaction_record.method == "Withdraw"
                # TODO ここ本当に必要か、必要なら他のW系には不要なのか
                and len(self.internal_txn_records) > 0
            ):
                # WBNB Withdraw
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_from,
                    self.transaction_record.txn_to,
                    str(abs(self.internal_txn_records[0].quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WBNB",
                    "WBNB",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

        wrapped_ftm_address = [
            "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",  # fantom
        ]
        lowercase_wrapped_ftm_address = [
            address.lower() for address in wrapped_ftm_address
        ]
        if (
            self.transaction_record
            and self.transaction_record.txn_to in lowercase_wrapped_ftm_address
        ):
            if self.transaction_record.method == "Deposit":
                # WFTM Deposit
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_to,
                    self.transaction_record.txn_from,
                    str(abs(self.transaction_record.quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WFTM",
                    "WFTM",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

            elif (
                self.transaction_record.method == "Withdraw"
                # TODO ここ本当に必要か、必要なら他のW系には不要なのか
                and len(self.internal_txn_records) > 0
            ):
                # WFTM Withdraw
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_from,
                    self.transaction_record.txn_to,
                    str(abs(self.internal_txn_records[0].quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WFTM",
                    "WFTM",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

        wrapped_avax_address = [
            "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",  # avalanche
        ]
        lowercase_wrapped_avax_address = [
            address.lower() for address in wrapped_avax_address
        ]
        if (
            self.transaction_record
            and self.transaction_record.txn_to in lowercase_wrapped_avax_address
        ):
            if self.transaction_record.method == "Deposit":
                # WAVAX Deposit
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_to,
                    self.transaction_record.txn_from,
                    str(abs(self.transaction_record.quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WAVAX",
                    "WAVAX",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

            elif (
                self.transaction_record.method == "Withdraw"
                # TODO ここ本当に必要か、必要なら他のW系には不要なのか
                and len(self.internal_txn_records) > 0
            ):
                # WAVAX Withdraw
                csv_record = [
                    self.txhash,
                    self.unix_timestamp,
                    self.date_time,
                    self.transaction_record.txn_from,
                    self.transaction_record.txn_to,
                    str(abs(self.internal_txn_records[0].quantity)),
                    self.transaction_record.historical_price_eth,
                    self.transaction_record.txn_to,
                    "WAVAX",
                    "WAVAX",
                    self.private_note,
                ]
                tx_record = Erc20TxnRecord(
                    self.network,
                    self.my_address,
                    self.transaction_record.name,
                    [],
                    csv_record,
                )
                self.erc20_txn_records.append(tx_record)
                self.add_attributes(tx_record.attributes)

    def add_attributes(self, attributes: List[TradeAttribute]):
        for attribute in attributes:
            if attribute not in self.attributes:
                self.attributes.append(attribute)

    def validate(self):
        records = list()
        if self.transaction_record:
            records.append(self.transaction_record)
        records.extend(self.erc20_txn_records)
        records.extend(self.erc721_txn_records)
        records.extend(self.erc1155_txn_records)

        txhash = ""
        for record in records:
            if record.txhash != txhash and txhash != "":
                raise ValueError("Groupのtxhashが不一致")
            txhash = record.txhash

    def calc_trade(self, record: AbstractRecord):
        if is_transaction_record(record):
            if (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "購入"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "売却"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "転入"
            elif (
                TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "転送"
            else:
                return "実行"
        elif is_internal_txn_record(record):
            if (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "購入"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "売却"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "転入"
            elif (
                TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "転送"
            elif TradeAttribute.CREATE in record.attributes:
                return "実行"
            else:
                return "実行"
        elif is_erc20_txn_record(record):
            if record.txn_from != self.my_address and record.txn_to != self.my_address:
                return "削除"
            elif (
                TradeAttribute.OUTCOME in record.attributes
                and TradeAttribute.SELF in record.attributes
            ):
                return "転送"
            elif (
                TradeAttribute.INCOME in record.attributes
                and TradeAttribute.SELF in record.attributes
            ):
                return "転入"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "購入"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "売却"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "転入"
            elif (
                TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "転送"
            else:
                raise ValueError("tradeが判定できない")
        elif is_erc721_txn_record(record):
            if record.txn_from != self.my_address and record.txn_to != self.my_address:
                return "削除"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "物品購入"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "物品売却"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "物品転入"
            elif (
                TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "物品転送"
            elif (
                TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.SELF in record.attributes
            ):
                return "物品転送"
            else:
                raise ValueError("tradeが判定できない")
        elif is_erc1155_txn_record(record):
            if record.txn_from != self.my_address and record.txn_to != self.my_address:
                return "削除"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "物品購入"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "物品売却"
            elif (
                TradeAttribute.INCOME in self.attributes
                and TradeAttribute.INCOME in record.attributes
            ):
                return "物品転入"
            elif (
                TradeAttribute.OUTCOME in self.attributes
                and TradeAttribute.OUTCOME in record.attributes
            ):
                return "物品転送"
            else:
                raise ValueError("tradeが判定できない")
        else:
            raise Exception("unexpected record")

    def is_multi_trade(self):
        income_count = 0
        outcome_count = 0
        if self.transaction_record is not None:
            if TradeAttribute.OUTCOME in self.transaction_record.attributes:
                outcome_count = outcome_count + 1
            if TradeAttribute.INCOME in self.transaction_record.attributes:
                income_count = income_count + 1

        for record in self.internal_txn_records:
            if TradeAttribute.OUTCOME in record.attributes:
                outcome_count = outcome_count + 1
            if TradeAttribute.INCOME in record.attributes:
                income_count = income_count + 1

        for record in self.erc20_txn_records:
            if TradeAttribute.OUTCOME in record.attributes:
                outcome_count = outcome_count + 1
            if TradeAttribute.INCOME in record.attributes:
                income_count = income_count + 1

        return True if income_count >= 2 or outcome_count >= 2 else False

    def calc(self):
        if self.transaction_record is not None:
            self.transaction_record.trade = self.calc_trade(self.transaction_record)
        for record in self.internal_txn_records:
            record.trade = self.calc_trade(record)
        for record in self.erc20_txn_records:
            record.trade = self.calc_trade(record)
            # 不具合があるのでコメントアウト、変更対象がお互い参照しあったり、３つ以上のときにおかしい
            # record.unit_price = self.get_rate_by_transaction_group(record)
        for record in self.erc721_txn_records:
            record.trade = self.calc_trade(record)
        for record in self.erc1155_txn_records:
            record.trade = self.calc_trade(record)
        self.validate()

    def to_output_records(self) -> List[OutputRecord]:
        if (
            self.network["name"] == "avalanche"
            and self.txhash
            == "0x4c2941a9a6dbc19294e041b052cad5231d8f2cfd909818ef8d970a3077e0a786"
        ):
            breakpoint()
        records: List[OutputRecord] = list()
        if self.transaction_record:
            record = OutputRecord(
                self.network["name"],
                self.my_address,
                self.txhash,
                self.date_time,
                self.transaction_record.method,
                self.transaction_record.counterparty,
                "",
                self.transaction_record.trade,
                "",
                self.status,
                "",
                "",
                "",
                self.transaction_record.quantity,
                self.network["symbol"],
                self.transaction_record.unit_price,
                self.transaction_record.fiat_quantity,
                "USD",
                self.transaction_record.get_fee_quantity(),
                self.network["symbol"],
                self.transaction_record.unit_price,
                "",  # calc
                "USD",
                get_rate("USDJPY", self.transaction_record.get_trading_date(), rate_df),
                "",
                "",
                "",
                self.private_note,
            )
            records.append(record)

        for txn_record in self.internal_txn_records:
            record = OutputRecord(
                self.network["name"],
                self.my_address,
                self.txhash,
                self.date_time,
                self.method,
                txn_record.counterparty,
                "",
                txn_record.trade,
                "",
                self.status,
                "",
                "",
                "",
                txn_record.quantity,
                self.network["symbol"],
                txn_record.unit_price,
                txn_record.fiat_quantity,
                "USD",
                "",
                self.network["symbol"],
                "",
                "",  # calc
                "USD",
                get_rate("USDJPY", txn_record.get_trading_date(), rate_df),
                "",
                "",
                "",
                self.private_note,
            )

            records.append(record)

        for txn_record in self.erc20_txn_records:
            record = OutputRecord(
                self.network["name"],
                self.my_address,
                self.txhash,
                self.date_time,
                self.method,
                txn_record.counterparty,
                "",
                txn_record.trade,
                "",
                self.status,
                "",
                "",
                txn_record.adjustment_unit_price,
                txn_record.quantity,
                txn_record.token_symbol,
                txn_record.unit_price,
                txn_record.fiat_quantity,
                "USD",
                "",
                self.network["symbol"],
                "",
                "",  # calc
                "USD",
                get_rate("USDJPY", txn_record.get_trading_date(), rate_df),
                "",
                "",
                "",
                self.private_note,
            )

            records.append(record)

        for txn_record in self.erc721_txn_records:
            record = OutputRecord(
                self.network["name"],
                self.my_address,
                self.txhash,
                self.date_time,
                self.method,
                txn_record.counterparty,
                "",
                txn_record.trade,
                txn_record.token_id,
                self.status,
                "",
                "",
                "",
                "",  # txn_record.quantity 容量削減で空欄
                f"{txn_record.token_name}({txn_record.token_symbol})#{txn_record.token_id}(ERC721)",
                "",
                "",
                "USD",
                "",
                self.network["symbol"],
                "",
                "",  # calc
                "USD",
                get_rate("USDJPY", txn_record.get_trading_date(), rate_df),
                "",
                "",
                "",
                f"{txn_record.token_id}, {self.private_note}",
            )

            records.append(record)

        for txn_record in self.erc1155_txn_records:
            record = OutputRecord(
                self.network["name"],
                self.my_address,
                self.txhash,
                self.date_time,
                self.method,
                txn_record.counterparty,
                "",
                txn_record.trade,
                "",
                self.status,
                "",
                "",
                "",
                "" if txn_record.quantity == 1 else txn_record.quantity,
                f"{txn_record.token_name}({txn_record.token_symbol})#{txn_record.token_id}(ERC1151)",
                "",
                "",
                "USD",
                "",
                self.network["symbol"],
                "",
                "",  # calc
                "USD",
                get_rate("USDJPY", txn_record.get_trading_date(), rate_df),
                "",
                "",
                "",
                self.private_note,
            )

            records.append(record)

        return records


TransationRecordsMap = TypedDict(
    "TransationRecordsMap", {"network": Network, "records": List[AbstractRecord]}
)
