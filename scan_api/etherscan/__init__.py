import pprint  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from decimal import Decimal  # noqa: E402
from typing import (  # noqa: E402
    Dict,
    List,
    Literal,
    MutableSet,
    Optional,
    TypedDict,
    TypeGuard,
)

from util import api_base  # noqa: E402
from util.logger import get_logger
from util.util import timestamp_fromdatetime  # noqa: E402

from ..types import Scan
from ..util import wei_to_token, write_csv

logger = get_logger()


class GetBlocknoEtherscanApi(api_base.APIBase):
    """GetBlocknoEtherscanApi

    https://api.etherscan.io/api
       ?module=block
       &action=getblocknobytime
       &timestamp=1578638524
       &closest=before
       &apikey=YourApiKeyToken
    """

    def __init__(self, scan: Scan):
        self._url = scan.url
        self._key = scan.key

    def get_url_with_params(self, **kwargs):
        d = self.make_query_dict(
            module="block",
            action="getblocknobytime",
            timestamp=timestamp_fromdatetime(kwargs.get("timestamp")),
            closest="before",
            apikey=self._key,
        )
        url = self.make_url(self._url, d)

        print(kwargs.get("timestamp").strftime("%Y-%m-%d %H:%M:%S"))

        print(url)
        return url

    def parse(self, response):
        blockno = response["result"]

        self.__response__ = response
        return blockno

    def execute(self, **kwargs) -> int:
        """
        :param datetime timestamp: datetime
        :return: blockno
        :rtype: int
        """
        return super().execute(**kwargs)


class GetTxlistEtherscanApi(api_base.APIBase):
    # https://api.etherscan.io/api
    #    ?module=account
    #    &action=txlist
    #    &address=0xc5102fE9359FD9a28f877a67E36B0F050d81a3CC
    #    &startblock=0
    #    &endblock=99999999
    #    &page=1
    #    &offset=10
    #    &sort=asc
    #    &apikey=YourApiKeyToken
    def __init__(self, scan: Scan):
        self._url = scan.url
        self._key = scan.key

    def get_url_with_params(self, **kwargs):
        query_params = {
            "module": "account",
            "action": kwargs.get("action"),
            "address": kwargs.get("address"),
            "page": kwargs.get("page"),
            "offset": kwargs.get("offset"),
            "sort": "asc",
            "apikey": self._key,
        }

        if kwargs.get("startblock") is not None:
            query_params["startblock"] = kwargs.get("startblock")
        if kwargs.get("endblock") is not None:
            query_params["endblock"] = kwargs.get("endblock")

        d = self.make_query_dict(**query_params)
        url = self.make_url(self._url, d)
        print(url)
        return url

    def parse(self, response):
        result = response["result"]
        if result is None:
            print(response)

        self.__response__ = response
        return result

    def execute(self, **kwargs):
        """
        :action TYPE_ACTION action: action
        :param str address: address
        :param int startblock: startblock
        :param int endblock: endblock
        :return: result
        :rtype: Any
        """
        return super().execute(**kwargs)


def get_etherscan_txlist(
    scan: Scan,
    address: str,
    start_datetime: Optional[datetime],
    end_datetime: Optional[datetime],
    output_directory: str = "./output",
):
    ret = True

    output_directory_network = "/".join([output_directory, address, scan.network])

    get_blockno_api = GetBlocknoEtherscanApi(scan)
    get_txlist_api = GetTxlistEtherscanApi(scan)

    startblockno = None
    if start_datetime:
        startblockno = get_blockno_api.execute(
            timestamp=start_datetime.astimezone(timezone.utc)
        )

    endblockno = None
    if end_datetime:
        endblockno = get_blockno_api.execute(
            timestamp=end_datetime.astimezone(timezone.utc)
        )

    result: List[dict] = get_txlist_api.execute(
        action="txlist",
        address=address,
        startblock=startblockno,
        endblock=endblockno,
    )

    if result is None:
        ret = False
        result = []
    if len(result) > 0:
        pprint.pprint(result[0])
    field_names = [
        "blockHash",
        "blockNumber",
        "confirmations",
        "contractAddress",
        "cumulativeGasUsed",
        "from",
        "functionName",
        "gas",
        "gasPrice",
        "gasUsed",
        "hash",
        "isError",
        "methodId",
        "nonce",
        "timeStamp",
        "to",
        "transactionIndex",
        "txreceipt_status",
        "value",
    ]

    ignore_list = ["input", "gasPriceBid"]
    write_csv(
        "/".join([output_directory_network, "source"]),
        "txlist.csv",
        field_names,
        result,
        ignore_list,
    )

    # convert
    data = list()
    for row in result:
        new_row = dict()
        new_row["Txhash"] = row["hash"]
        new_row["Blockno"] = row["blockNumber"]
        new_row["UnixTimestamp"] = row["timeStamp"]
        timestamp_dt = datetime.fromtimestamp(float(row["timeStamp"]), timezone.utc)
        new_row["DateTime (UTC)"] = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
        new_row["From"] = row["from"]
        new_row["To"] = row["to"]
        new_row["ContractAddress"] = row["contractAddress"]
        new_row["Value_IN(TOKEN)"] = str(
            wei_to_token(
                (
                    row["value"]
                    if row["from"].lower() != address.lower()
                    and row["to"].lower() == address.lower()
                    else 0
                ),
                scan.decimals,
            )
        )
        new_row["Value_OUT(TOKEN)"] = str(
            wei_to_token(
                (
                    row["value"]
                    if row["to"].lower() != address.lower()
                    and row["from"].lower() == address.lower()
                    else 0
                ),
                scan.decimals,
            )
        )
        new_row["CurrentValue"] = ""
        new_row["TxnFee(TOKEN)"] = str(
            int(row["gasUsed"]) * wei_to_token(int(row["gasPrice"]), scan.decimals)
        )
        new_row["TxnFee(USD)"] = ""
        new_row["Historical $Price/TOKEN"] = ""
        new_row["Status"] = (
            ""
            if row["txreceipt_status"] == "1"
            else "Error(" + row["txreceipt_status"] + ")"
        )
        new_row["ErrCode"] = "" if row["txreceipt_status"] == "1" else "!Unknown!"
        new_row["Method"] = row["functionName"].split("(")[0]
        new_row["PrivateNote"] = ""

        data.append(new_row)

    field_names = [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime (UTC)",
        "From",
        "To",
        "ContractAddress",
        "Value_IN(TOKEN)",
        "Value_OUT(TOKEN)",
        "CurrentValue",
        "TxnFee(TOKEN)",
        "TxnFee(USD)",
        "Historical $Price/TOKEN",
        "Status",
        "ErrCode",
        "Method",
        "PrivateNote",
    ]

    write_csv(
        output_directory_network,
        "transactions.csv",
        field_names,
        data,
    )

    return ret


def get_etherscan_txlist_internal(
    scan: Scan,
    address: str,
    start_datetime: Optional[datetime],
    end_datetime: Optional[datetime],
    output_directory: str,
):
    ret = True

    output_directory_network = "/".join([output_directory, address, scan.network])

    get_blockno_api = GetBlocknoEtherscanApi(scan)
    get_txlist_api = GetTxlistEtherscanApi(scan)

    startblockno = None
    if start_datetime:
        startblockno = get_blockno_api.execute(
            timestamp=start_datetime.astimezone(timezone.utc)
        )

    endblockno = None
    if end_datetime:
        endblockno = get_blockno_api.execute(
            timestamp=end_datetime.astimezone(timezone.utc)
        )

    result = get_txlist_api.execute(
        action="txlistinternal",
        address=address,
        startblock=startblockno,
        endblock=endblockno,
    )

    if result is None:
        ret = False
        result = []
    if len(result) > 0:
        pprint.pprint(result[0])
    field_names = [
        "blockNumber",
        "contractAddress",
        "errCode",
        "from",
        "gas",
        "gasUsed",
        "hash",
        "isError",
        "timeStamp",
        "to",
        "traceId",
        "type",
        "value",
    ]
    ignore_list = ["input"]
    write_csv(
        "/".join([output_directory_network, "source"]),
        "txlist_internal.csv",
        field_names,
        result,
        ignore_list,
    )

    # convert
    data = list()
    for row in result:
        new_row = dict()
        new_row["Txhash"] = row["hash"]
        new_row["Blockno"] = row["blockNumber"]
        new_row["UnixTimestamp"] = row["timeStamp"]
        timestamp_dt = datetime.fromtimestamp(float(row["timeStamp"]), timezone.utc)
        new_row["DateTime (UTC)"] = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
        new_row["ParentTxFrom"] = ""
        new_row["ParentTxTo"] = ""
        new_row["ParentTxTOKEN_Value"] = ""
        new_row["From"] = row["from"]
        new_row["TxTo"] = row["to"]
        new_row["ContractAddress"] = row["contractAddress"]
        new_row["Value_IN(TOKEN)"] = str(
            wei_to_token(
                (
                    row["value"]
                    if row["from"].lower() != address.lower()
                    and row["to"].lower() == address.lower()
                    else 0
                ),
                scan.decimals,
            )
        )
        new_row["Value_OUT(TOKEN)"] = str(
            wei_to_token(
                (
                    row["value"]
                    if row["to"].lower() != address.lower()
                    and row["from"].lower() == address.lower()
                    else 0
                ),
                scan.decimals,
            )
        )
        new_row["CurrentValue"] = ""
        new_row["Historical $Price"] = ""
        new_row["Status"] = (
            "" if row["isError"] == "0" else "Error(" + row["isError"] + ")"
        )
        new_row["ErrCode"] = "" if row["isError"] == "0" else "!Unknown!"
        new_row["Type"] = row["type"]
        new_row["PrivateNote"] = ""

        data.append(new_row)

    field_names = [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime (UTC)",
        "ParentTxFrom",
        "ParentTxTo",
        "ParentTxTOKEN_Value",
        "From",
        "TxTo",
        "ContractAddress",
        "Value_IN(TOKEN)",
        "Value_OUT(TOKEN)",
        "CurrentValue",
        "Historical $Price",
        "Status",
        "ErrCode",
        "Type",
        "PrivateNote",
    ]

    write_csv(
        output_directory_network,
        "internals.csv",
        field_names,
        data,
    )

    return ret


def get_etherscan_txlist_token(
    scan: Scan,
    address: str,
    start_datetime: Optional[datetime],
    end_datetime: Optional[datetime],
    output_directory: str,
):
    ret = True

    output_directory_network = "/".join([output_directory, address, scan.network])

    get_blockno_api = GetBlocknoEtherscanApi(scan)
    get_txlist_api = GetTxlistEtherscanApi(scan)

    startblockno = None
    if start_datetime:
        startblockno = get_blockno_api.execute(
            timestamp=start_datetime.astimezone(timezone.utc)
        )

    endblockno = None
    if end_datetime:
        endblockno = get_blockno_api.execute(
            timestamp=end_datetime.astimezone(timezone.utc)
        )

    result = get_txlist_api.execute(
        action="tokentx",
        address=address,
        startblock=startblockno,
        endblock=endblockno,
    )

    if result is None:
        ret = False
        result = []

    rows = []
    for row in result:
        rows.append(row)

    if len(rows) > 0:
        pprint.pprint(rows[0])
    field_names = [
        "blockHash",
        "blockNumber",
        "confirmations",
        "contractAddress",
        "cumulativeGasUsed",
        "from",
        "gas",
        "gasPrice",
        "gasUsed",
        "hash",
        "nonce",
        "timeStamp",
        "to",
        "tokenDecimal",
        "tokenName",
        "tokenSymbol",
        "transactionIndex",
        "value",
    ]

    ignore_list = ["input"]
    write_csv(
        "/".join([output_directory_network, "source"]),
        "txlist_token.csv",
        field_names,
        rows,
        ignore_list,
    )

    # convert
    data = list()
    for row in rows:
        new_row = dict()
        new_row["Txhash"] = row["hash"]
        new_row["Blockno"] = row["blockNumber"]
        new_row["UnixTimestamp"] = row["timeStamp"]
        timestamp_dt = datetime.fromtimestamp(float(row["timeStamp"]), timezone.utc)
        new_row["DateTime (UTC)"] = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
        new_row["From"] = row["from"]
        new_row["To"] = row["to"]
        new_row["TokenValue"] = str(
            wei_to_token(
                row["value"],
                Decimal(row["tokenDecimal"]),
            )
        )
        new_row["USDValueDayOfTx"] = ""
        new_row["ContractAddress"] = row["contractAddress"]
        new_row["TokenName"] = row["tokenName"]
        new_row["TokenSymbol"] = row["tokenSymbol"]
        new_row["PrivateNote"] = ""

        data.append(new_row)

    field_names = [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime (UTC)",
        "From",
        "To",
        "TokenValue",
        "USDValueDayOfTx",
        "ContractAddress",
        "TokenName",
        "TokenSymbol",
        "PrivateNote",
    ]

    write_csv(
        output_directory_network,
        "erc20.csv",
        field_names,
        data,
    )
    return ret


def get_etherscan_txlist_tokennft(
    scan: Scan,
    address: str,
    start_datetime: Optional[datetime],
    end_datetime: Optional[datetime],
    output_directory: str,
):
    ret = True

    output_directory_network = "/".join([output_directory, address, scan.network])

    get_blockno_api = GetBlocknoEtherscanApi(scan)
    get_txlist_api = GetTxlistEtherscanApi(scan)

    startblockno = None
    if start_datetime:
        startblockno = get_blockno_api.execute(
            timestamp=start_datetime.astimezone(timezone.utc)
        )

    endblockno = None
    if end_datetime:
        endblockno = get_blockno_api.execute(
            timestamp=end_datetime.astimezone(timezone.utc)
        )

    result = get_txlist_api.execute(
        action="tokennfttx",
        address=address,
        startblock=startblockno,
        endblock=endblockno,
    )

    if result is None:
        ret = False
        result = []

    rows = []
    for row in result:
        rows.append(row)

    if len(rows) > 0:
        pprint.pprint(rows[0])
    field_names = [
        "blockHash",
        "blockNumber",
        "confirmations",
        "contractAddress",
        "cumulativeGasUsed",
        "from",
        "gas",
        "gasPrice",
        "gasUsed",
        "hash",
        "nonce",
        "timeStamp",
        "to",
        "tokenDecimal",
        "tokenID",
        "tokenName",
        "tokenSymbol",
        "transactionIndex",
    ]
    ignore_list = ["input"]
    write_csv(
        "/".join([output_directory_network, "source"]),
        "txlist_tokennft.csv",
        field_names,
        rows,
        ignore_list,
    )

    # convert
    data = list()
    for row in rows:
        new_row = dict()
        new_row["Txhash"] = row["hash"]
        new_row["Blockno"] = row["blockNumber"]
        new_row["UnixTimestamp"] = row["timeStamp"]
        timestamp_dt = datetime.fromtimestamp(float(row["timeStamp"]), timezone.utc)
        new_row["DateTime (UTC)"] = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
        new_row["From"] = row["from"]
        new_row["To"] = row["to"]
        new_row["ContractAddress"] = row["contractAddress"]
        new_row["TokenId"] = row["tokenID"]
        new_row["TokenName"] = row["tokenName"]
        new_row["TokenSymbol"] = row["tokenSymbol"]
        new_row["PrivateNote"] = ""

        data.append(new_row)

    field_names = [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime (UTC)",
        "From",
        "To",
        "ContractAddress",
        "TokenId",
        "TokenName",
        "TokenSymbol",
        "PrivateNote",
    ]
    write_csv(
        output_directory_network,
        "erc721.csv",
        field_names,
        data,
    )

    return ret


def get_etherscan_txlist_token1155(
    scan: Scan,
    address: str,
    start_datetime: Optional[datetime],
    end_datetime: Optional[datetime],
    output_directory: str,
):
    ret = True

    output_directory_network = "/".join([output_directory, address, scan.network])

    get_blockno_api = GetBlocknoEtherscanApi(scan)
    get_txlist_api = GetTxlistEtherscanApi(scan)

    startblockno = None
    if start_datetime:
        startblockno = get_blockno_api.execute(
            timestamp=start_datetime.astimezone(timezone.utc)
        )

    endblockno = None
    if end_datetime:
        endblockno = get_blockno_api.execute(
            timestamp=end_datetime.astimezone(timezone.utc)
        )

    result = get_txlist_api.execute(
        action="token1155tx",
        address=address,
        startblock=startblockno,
        endblock=endblockno,
    )

    if result is None:
        ret = False
        result = []

    rows = []
    for row in result:
        rows.append(row)

    if len(rows) > 0:
        pprint.pprint(rows[0])
    field_names = [
        "blockHash",
        "blockNumber",
        "confirmations",
        "contractAddress",
        "cumulativeGasUsed",
        "from",
        "gas",
        "gasPrice",
        "gasUsed",
        "hash",
        "nonce",
        "timeStamp",
        "to",
        "tokenDecimal",
        "tokenID",
        "tokenName",
        "tokenSymbol",
        "tokenValue",
        "transactionIndex",
    ]

    ignore_list = ["input"]
    write_csv(
        "/".join([output_directory_network, "source"]),
        "txlist_token1155.csv",
        field_names,
        rows,
        ignore_list,
    )

    # convert
    data = list()
    for row in rows:
        new_row = dict()
        new_row["Txhash"] = row["hash"]
        new_row["Blockno"] = row["blockNumber"]
        new_row["UnixTimestamp"] = row["timeStamp"]
        timestamp_dt = datetime.fromtimestamp(float(row["timeStamp"]), timezone.utc)
        new_row["DateTime (UTC)"] = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
        new_row["From"] = row["from"]
        new_row["To"] = row["to"]
        new_row["ContractAddress"] = row["contractAddress"]
        new_row["TokenId"] = row["tokenID"]
        new_row["TokenName"] = row["tokenName"]
        new_row["TokenSymbol"] = row["tokenSymbol"]
        new_row["PrivateNote"] = ""

        data.append(new_row)

    field_names = [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime (UTC)",
        "From",
        "To",
        "ContractAddress",
        "TokenId",
        "TokenName",
        "TokenSymbol",
        "PrivateNote",
    ]

    write_csv(
        output_directory_network,
        "erc1155.csv",
        field_names,
        data,
    )
    return ret
