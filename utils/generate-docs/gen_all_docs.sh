#!/bin/bash

# エラーが発生したら即座に終了
set -e

# 仮想環境が存在しない場合は作成
if [ ! -d ".venv" ]; then
    echo "仮想環境を作成します..."
    python3 -m venv .venv
fi

# 仮想環境をアクティベート
source .venv/bin/activate

echo "依存パッケージをインストールします..."
pip install -r requirements.txt 2>/dev/null || echo "requirements.txtが見つからないか、インストールに失敗しました"

# Pythonスクリプトを実行
echo "ドキュメント生成を開始します..."

echo "1. 列挙型のドキュメントを生成中..."
python3 utils/generate-docs/gen_enums_docs.py

echo "2. ファイル型のドキュメントを生成中..."
python3 utils/generate-docs/gen_files_docs.py

echo "3. 型定義のドキュメントを生成中..."
python3 utils/generate-docs/gen_types_docs.py

echo "4. プリミティブ型のドキュメントを生成中..."
python3 utils/generate-docs/gen_primitive_docs.py

echo "ドキュメント生成が完了しました"

# 仮想環境を非アクティブ化
deactivate