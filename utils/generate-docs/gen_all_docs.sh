#!/bin/bash

# エラーが発生したら即座に終了
set -e

# ヘルプメッセージの表示
show_help() {
    cat << EOF
使用方法: $(basename "$0") [仮想環境名] [オプション]

仮想環境名を指定してドキュメントを生成します。
仮想環境名が指定されない場合は'.venv'を使用します。

オプション:
    -h, --help    このヘルプメッセージを表示して終了

例:
    $(basename "$0")          # デフォルトの'.venv'を使用
    $(basename "$0") my-venv  # 'my-venv'を使用
EOF
}

# コマンドライン引数の処理
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
esac

# スクリプトの場所を取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# プロジェクトルートディレクトリに移動
cd "$PROJECT_ROOT" || exit 1

# デフォルトの仮想環境名
VENV_NAME="${1:-.venv}"

# 仮想環境が存在しない場合は作成
if [ ! -d "$VENV_NAME" ]; then
    echo "仮想環境 ($VENV_NAME) を作成します..."
    python3 -m venv "$VENV_NAME"
fi

# 仮想環境をアクティベート
source "$VENV_NAME/bin/activate"

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

echo "5. オブジェクト型のドキュメントを生成中..."
python3 utils/generate-docs/gen_objects_docs.py

echo "ドキュメント生成が完了しました"

# 仮想環境を非アクティブ化
deactivate