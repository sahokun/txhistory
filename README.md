# txhistory

## 使い方

## setup

```shell
    pip install --upgrade pip
    sudo pip install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-district.txt
```

## get_scan_csv

1. etherscan 系を使う場合は scan_api/types の各ネットワークの key を設定
2. run_get_scan_csv.py の scans/address/start_jst/end_jst を調整
3. RUN: get_scan_csv
4. output に csv が出力される

## make_history

1. 必要に応じて data/rate.xlsx を調整
2. data に get_scan_csv の出力物をコピー 例：data/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
3. RUN: make_history
4. output に xlsx が出力される　※データ量によってはかなり時間がかかるので注意
