import schema_config

# スキーマの$idからベースURLを除去して相対パスを取得する
def extract_ref_relative_path(schema_id: str) -> str:
    """
    $refパスからベースURLを除去して相対パスを取得する
    例: "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
    → "objects/StockClass.schema.json"
    """
    if schema_id.startswith(schema_config.SCHEMA_BASE_URL):
        return f"../{schema_id[len(schema_config.SCHEMA_BASE_URL + '/'):]}"
    return schema_id

# スキーマの$idから拡張子を除いたファイル名部分を抽出する
def extract_file_name_wo_extension(schema_id: str) -> str:
    """
    $refパスから最後のファイル名部分を抽出する
    例: "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
    → "StockClass"
    """
    # パスの最後のファイル名を取得
    filename = schema_id.split('/')[-1]
    # 設定された拡張子を除去
    return filename.replace(schema_config.SCHEMA_FILE_EXTENSION, '')