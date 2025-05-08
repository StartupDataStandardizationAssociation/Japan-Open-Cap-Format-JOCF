import schema_config

# スキーマの$idからベースURLを除去して相対パスを取得する
def extract_ref_relative_path(schema_id: str) -> str:
    """
    $refパスからベースURLを除去して相対パスを取得する
    例: "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
    → "objects/StockClass.schema.json"
    """
    if not schema_id.startswith(schema_config.SCHEMA_BASE_URL):
        raise ValueError(f"スキーマID '{schema_id}' は基準となるURL '{schema_config.SCHEMA_BASE_URL}' で始まっていません")

    # スキーマIDからベースURLを除去して相対パスを取得
    schema_relative_path = schema_id[len(schema_config.SCHEMA_BASE_URL + '/'):]
    # schema_relative_pathからroot_directoryまでの深さを算出
    depth = len(schema_relative_path.split('/')) - 1
    # 深さに応じて../を生成
    root_relative_path = '../' * depth
    return _extract_ref_relative_path_with_root(schema_id, root_relative_path)

def _extract_ref_relative_path_with_root(schema_id: str, root_relative_path:str) -> str:
    """
    $refパスからベースURLを除去して相対パスを取得する
    例: "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
    → "../objects/StockClass.schema.json"
    """
    if not schema_id.startswith(schema_config.SCHEMA_BASE_URL):
        raise ValueError(f"スキーマID '{schema_id}' は基準となるURL '{schema_config.SCHEMA_BASE_URL}' で始まっていません")
    
    return f"{root_relative_path}{schema_id[len(schema_config.SCHEMA_BASE_URL + '/'):]}"


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


def convert_extension_from_schema_path_to_md(schema_path: str) -> str:
    """
    スキーマファイルのパスからMarkdownファイルのパスに変換する
    例: objects/StockClass.schema.json → objects/StockClass.md
    """
    return schema_path.replace(schema_config.SCHEMA_FILE_EXTENSION, '.md')