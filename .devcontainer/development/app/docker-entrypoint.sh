#!/bin/bash
set -e

echo "docker-entrypoint.sh"

# 初回起動判定用のファイルの存在を確認
if [ ! -f /.first_run ]; then
    echo "first run"
    # 初回起動時の処理
    cd /src || exit
    echo "pip install --upgrade pip"
    pip install --upgrade pip
    echo "pip install virtualenv"
    sudo pip install virtualenv

    # venvディレクトリの存在を確認
    if [ ! -d "venv" ]; then 
        echo "virtualenv venv"
        virtualenv venv
        echo "source venv/bin/activate"
        # shellcheck source=/dev/null
        source venv/bin/activate
        echo "pip install --upgrade pip"
        pip install --upgrade pip
    fi

    # 初回起動判定用のファイルを作成
    echo "sudo touch /.first_run"
    sudo touch /.first_run
fi

echo "exec @"
# 元々のENTRYPOINTを実行 (exec "$@" はCMDで指定されたコマンドを実行)
exec "$@"