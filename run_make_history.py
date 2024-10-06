import copy
import csv
import os
import re
import sys
import time
from datetime import datetime, timedelta
from itertools import groupby
from typing import List, Set, TypedDict

from models import (
    BASE_SYMBOLS,
    NETWORKS,
    AbstractRecord,
    AnalyzeCsvError,
    Erc20TxnRecord,
    Erc721TxnRecord,
    Erc1155TxnRecord,
    InternalTxnRecord,
    Network,
    OutputRecord,
    TransactionGroup,
    TransactionRecord,
    TransationFileMap,
    TransationRecordsMap,
)
from util.logger import get_logger, setup_logger
from util.util import to_decimal
from wopenpyxl import WOpenpyxl

setup_logger()
logger = get_logger()


PATH_DATA = "./data"

START_ROW_IDX = 3

TARGET_FILES: List[TransationFileMap] = [
    {"class": [TransactionRecord], "file_name": "transactions.csv"},
    {"class": [InternalTxnRecord], "file_name": "internals.csv"},
    {"class": [Erc20TxnRecord], "file_name": "erc20.csv"},
    {"class": [Erc721TxnRecord], "file_name": "erc721.csv"},
    {"class": [Erc1155TxnRecord], "file_name": "erc1155.csv"},
    {"class": [Erc721TxnRecord, Erc1155TxnRecord], "file_name": "nfts.csv"},
]

BASIS_DATE = datetime.now()
BASIS_PERF_COUNTER = time.perf_counter()


def collect_transaction_records(
    network: Network, address: str
) -> List[TransationRecordsMap]:
    network_path = os.path.join(PATH_DATA, address, network["name"])

    name = address
    name_file = next(
        filter(lambda _: _.endswith(".name"), os.listdir(network_path)), None
    )
    if name_file:
        name = os.path.splitext(".name")

    records: List[AbstractRecord] = list()
    for target_file in TARGET_FILES:
        target_path = os.path.join(network_path, target_file["file_name"])
        logger.info(f"check {target_path}")
        if os.path.exists(target_path):
            logger.info(f"process {target_path}")
            with open(target_path, encoding="utf8", newline="") as f:
                csvreader = csv.reader(f)
                content = [row for row in csvreader]  # 各年のデータを要素とするリスト
                # logger.info(content)
                count = -1
                for row in content:
                    row_backup = copy.copy(row)
                    count = count + 1
                    if count == 0:
                        header = row
                        continue
                    transaction_class_list = target_file["class"]
                    for transaction_class in transaction_class_list:
                        try:
                            record: List[AbstractRecord] = transaction_class(
                                network, address, name, header, row
                            )
                            if not record.is_skip:
                                records.append(record)
                            else:
                                print("skip records.append")
                        except Exception as e:
                            import traceback

                            traceback.print_exc()
                            logger.info("例外args:", e.args)
                            logger.info("Analyze CSV Error!")
                            logger.info(
                                f'target_path: {target_path}, network: {network["name"]}, address: {address}'
                            )
                            logger.info(header)
                            logger.info(row_backup)
                            raise AnalyzeCsvError(row_backup)
                        finally:
                            pass
                        # pprint.pprint(vars(record))
        else:
            logger.info(
                f'not found {target_file["file_name"]} at {network["name"]}:{address}'
            )
    return records


def collect_transaction_records_for_networks(address: str):
    records_map_list: List[TransationRecordsMap] = list()
    for network in NETWORKS:
        network_path = os.path.join(PATH_DATA, address, network["name"])
        logger.info(f"check {network_path}")

        if os.path.exists(network_path):
            logger.info(f"process {network_path}")
            records = collect_transaction_records(network, address)
            records_map = {"network": network, "records": records}
            records_map_list.append(records_map)

    return records_map_list


def get_used_symbols(groups: List[TransactionGroup]):
    """
    トランザクションで利用されるシンボル名を集める
    """
    symbols = list()
    for group in groups:
        for record in group.erc20_txn_records:
            symbols.append(record.token_symbol)

    symbols.sort()
    unique_symbols = list()
    unique_symbols.extend(BASE_SYMBOLS)
    for key, g in groupby(symbols):
        unique_symbols.append(key)

    return unique_symbols


def attach_symbols(
    book: WOpenpyxl, sheet_name: str, symbols: List[str], pos_extend: int
) -> tuple[int, int]:
    """
    transactionsシートの後ろの列にシンボルを追加する
    """
    book.set_active_sheet(sheet_name)
    ws = book.active_sheet

    start_col = 0
    values = []
    # 1行目のみが対象
    for row in ws.iter_rows(min_row=1, max_row=1):
        # 列を走査
        for i, col in enumerate(row[(pos_extend - 1) :]):
            # private_noteを最後の列として判断
            # if is_reach:
            # すでに値がある場合は残して、シンボル一覧から削除
            if col.value != "":
                value = col.value.replace("(amt)", "").replace("(ave)", "")
                if value in symbols:
                    symbols.remove(value)
                # シンボル開始位置更新
                start_col = (pos_extend + i) + 1

    for i, symbol in enumerate(symbols):
        if symbol not in values:
            ws.cell(1, start_col, symbol + "(amt)")
            ws.cell(2, start_col, 0)
            ws.cell(1, start_col + 1, symbol + "(ave)")
            ws.cell(2, start_col + 1, 0)
            start_col = start_col + 2

    return_value2 = start_col

    # logger.info(values)
    return return_value2


def alpha2num(alpha):
    num = 0
    for index, item in enumerate(list(alpha)):
        num += pow(26, len(alpha) - index - 1) * (ord(item) - ord("A") + 1)
    return num


def num2alpha(num):
    if num <= 26:
        return chr(64 + num)
    elif num % 26 == 0:
        return num2alpha(num // 26 - 1) + chr(90)
    else:
        return num2alpha(num // 26) + chr(64 + num % 26)


def spread_formula_symbol(
    book: WOpenpyxl, start_symbol_col_idx: int, end_symbol_col_idx: int
):
    def alphabet_replacer(col_index: int):
        def alphabet_increment(matchobj):
            place_holder = matchobj.group(1)[1:-1]
            number_value = alpha2num(place_holder)
            alphabet_value = num2alpha(number_value + col_index - start_symbol_col_idx)
            return alphabet_value

        return alphabet_increment

    regex_string_alphabet = "({[A-Z]+})"
    book.set_active_sheet("template_temp")

    # まずは横にのばしてから、もともとの縦に伸ばすやつを実行する
    logger.info(f"start_symbol_col_idx: {start_symbol_col_idx}")
    start_symbol_col_idx_plus1 = start_symbol_col_idx + 1
    for c in range(start_symbol_col_idx, start_symbol_col_idx_plus1 + 1):
        template_value = book.get_value(START_ROW_IDX, c)
        template_value = (
            template_value.replace("'", "")
            if template_value is not None and isinstance(template_value, str)
            else ""
        )
        is_template = template_value.startswith("=")

        if is_template:
            max_cols = end_symbol_col_idx
            count_symbols = int((max_cols - start_symbol_col_idx - 1) / 2)
            logger.info(f"template_value: {template_value}")
            logger.info(f"max_cols: {max_cols}")
            logger.info(f"start_symbol_col_idx: {start_symbol_col_idx}")
            logger.info(f"(max_cols - start_symbol_col_idx) / 2: {count_symbols}")
            for count in range(0, count_symbols + 1):
                col_idx = c + (count * 2)
                result = re.sub(
                    regex_string_alphabet,
                    alphabet_replacer(col_idx - (c - start_symbol_col_idx)),
                    template_value,
                )
                # 本来はquotePrefix=True→シングルクオート勝手につくがしたいが
                # なぜかそれだとうまく動作せず、quotePrefixそのままだとシングルクオートが二重につく
                # quotePrefix=Falseにするとなぜか正しく動く
                book.get_cell(START_ROW_IDX, col_idx).quotePrefix = False
                book.set_value(START_ROW_IDX, col_idx, f"'{result}")


def spread_formula(book: WOpenpyxl, sheet_name: str):
    def number_replacer(row_index: int):
        def number_increment(matchobj):
            place_holder = matchobj.group(1)[1:-1]
            number_value = int(place_holder)
            return str(number_value + row_index - START_ROW_IDX)

        return number_increment

    regex_string_number = "({[0-9]+})"
    template_sheet = book.get_sheet("template_temp")
    # templateの横幅取得
    max_cols = template_sheet.max_column

    book.set_active_sheet(sheet_name)
    for c in range(1, max_cols + 1):
        # if c == 100:
        #     return

        template_value = template_sheet.cell(START_ROW_IDX, c).value
        template_value = (
            template_value.replace("'", "")
            if template_value is not None and isinstance(template_value, str)
            else ""
        )
        is_template = template_value.startswith("=")

        if is_template:
            logger.info(f"c={c}")
            # logger.info(f"template_value: {template_value}")
            max_rows = book.max_rows()
            for r in range(START_ROW_IDX, max_rows + 1):
                result = re.sub(regex_string_number, number_replacer(r), template_value)
                book.set_value(r, c, result)
                # logger.info(result)


def spread_cell_format(book: WOpenpyxl, sheet_name: str):
    target_column_idx = {
        11: "0.000000",  # K
        12: "0.000000",  # L
        13: "0.000000",  # M
        14: "0.000000",  # N
        15: "0.000000",  # O
        16: "0.000000",  # P
        17: "0.000000",  # Q
        19: "0.000000",  # S
        21: "0.000000",  # U
        22: "0.000000",  # V
        24: "0.000000",  # X
        25: "0.00",  # Y
        26: "0.00",  # Z
        27: "0.00",  # AA
        28: "0.00",  # AB
        29: "0.00",  # AC
    }
    book.set_active_sheet(sheet_name)
    max_rows = book.max_rows()

    for r in range(START_ROW_IDX, max_rows + 1):
        for key, value in target_column_idx.items():
            book.active_sheet.cell(r, key).number_format = value


def get_elapsed_time(basis_time: float):
    now_time = time.perf_counter()

    diff_time = now_time - basis_time
    seconds = int(diff_time + 0.5)  # 秒数を四捨五入
    h = seconds // 3600  # 時の取得
    m = (seconds - h * 3600) // 60  # 分の取得
    s = seconds - h * 3600 - m * 60  # 秒の取得

    return f"{h:02}:{m:02}:{s:02}"


def bundle_transaction_groups(records: List[AbstractRecord]):
    groups: List[TransactionGroup] = list()
    records.sort(key=lambda x: x.txhash)
    for key, group_by_txhash in groupby(records, key=lambda x: x.txhash):
        records_by_txhash = list(group_by_txhash)
        # logger.info(f"key: {key}, count: {len(records_by_txhash)}")
        # for record_by_txhash in records_by_txhash:
        #     logger.info(record_by_txhash)
        group = TransactionGroup()
        group.add_records(records_by_txhash)
        group.calc()
        groups.append(group)

    groups.sort(key=lambda x: int(x.unix_timestamp))
    return groups


def convert_group_to_csv_data(groups: List[TransactionGroup]):
    output_records: List[OutputRecord] = list()
    for group in groups:
        output_records.extend(group.to_output_records())

    data_rows: List[List[str]] = list()
    for output_record in output_records:
        data_rows.append(output_record.to_csv_row())

    return data_rows


def get_symbol_extend_position(
    book: WOpenpyxl,
) -> int:
    """
    private_note列の位置を調べる
    """
    book.set_active_sheet("template")
    ws = book.active_sheet

    # 1行目のみが対象
    for row in ws.iter_rows(min_row=1, max_row=1):
        # 列を走査
        for i, col in enumerate(row):
            if col.value == "private_note":
                return col.col_idx + 1


def output_processed_records(
    address: str, records_map_list: List[TransationRecordsMap]
):
    book = WOpenpyxl("./template.xlsx")
    file_name = f'{BASIS_DATE.strftime("%Y%m%d%H%M%S")}-{address}.xlsx'
    logger.info(f"output {file_name}")
    for records_map in records_map_list:
        network = records_map["network"]
        records = records_map["records"]

        groups: List[TransactionGroup] = bundle_transaction_groups(records)
        data_rows: List[List[str]] = convert_group_to_csv_data(groups)

        sheet_name = network["name"]
        logger.info(f"sheet_name: {sheet_name}")

        book.set_active_sheet("template")
        pos_extend = get_symbol_extend_position(book)
        book.copy_worksheet(book.active_sheet, sheet_name)
        book.set_active_sheet(sheet_name)
        book.delete_rows(START_ROW_IDX)
        book.append(data_rows)

        symbols = get_used_symbols(groups)
        end_symbol_col_idx = attach_symbols(book, sheet_name, symbols, pos_extend)
        logger.info(
            f"end attach_symbols({sheet_name}): {get_elapsed_time(BASIS_PERF_COUNTER)}"
        )

        book.set_active_sheet("template")
        book.copy_worksheet(book.active_sheet, "template_temp")

        spread_formula_symbol(book, pos_extend, end_symbol_col_idx)
        logger.info(
            f"end spread_formula_symbol({sheet_name}): {get_elapsed_time(BASIS_PERF_COUNTER)}"
        )
        spread_formula(book, sheet_name)
        logger.info(
            f"end spread_formula({sheet_name}): {get_elapsed_time(BASIS_PERF_COUNTER)}"
        )
        book.remove_sheet("template_temp")
        spread_cell_format(book, sheet_name)
        logger.info(
            f"end spread_cell_format({sheet_name}): {get_elapsed_time(BASIS_PERF_COUNTER)}"
        )

    book.save_as("./output/" + file_name)


def process_transaction_records():
    # ./data
    if os.path.exists(PATH_DATA):
        logger.info(f"check {PATH_DATA}")
        result_list = os.listdir(PATH_DATA)
        # 対象ディレクトリからディレクトリ一覧（アドレス）を取得
        address_directories = [
            f
            for f in result_list
            if os.path.isdir(os.path.join(PATH_DATA, f))
            and not os.path.join(PATH_DATA, f).endswith(".bak")
        ]

        for address in address_directories:
            logger.info(f"process {address}")
            records_map_list = collect_transaction_records_for_networks(address)
            output_processed_records(address, records_map_list)


def main(args):
    logger.info(f"start run_make_history: {datetime.now()}")

    process_transaction_records()

    logger.info(f"end {datetime.now()}({get_elapsed_time(BASIS_PERF_COUNTER)})")


if __name__ == "__main__":
    args = sys.argv
    if 1 <= len(args):
        main(args)
    else:
        logger.info("Arguments are too short")
