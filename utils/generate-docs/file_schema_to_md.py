#!/usr/bin/env python3

import argparse
import json
import os.path
import sys
from typing import Dict, Any
import schema_config
from property_util import get_property_type
from schema_id_util import extract_ref_relative_path, extract_file_name_wo_extension, convert_extension_from_schema_path_to_md

def validate_json_schema(schema: Dict[str, Any]) -> bool:
    """
    JSONスキーマの基本的な妥当性をチェックする
    """
    required_fields = ['title', 'properties']
    return all(field in schema for field in required_fields)

def is_required_property(prop_name: str, schema: Dict[str, Any]) -> str:
    """
    プロパティが必須かどうかを判定する
    """
    required = schema.get('required', [])
    return 'Yes' if prop_name in required else 'No'

def generate_markdown(schema: Dict[str, Any]) -> str:
    """
    JSONスキーマからMarkdown形式のドキュメントを生成する
    """
    md_lines = []
    
    # Schema Name
    md_lines.append(f"# {schema.get('title', 'Untitled Schema')}")
    md_lines.append("")
    
    # Schema ID
    if '$id' in schema:
        md_lines.append(f"ID = `{schema['$id']}`")
        md_lines.append("")
    
    # Description
    description = schema.get('description')
    if description:
        md_lines.append("## Description")
        md_lines.append(description)
        md_lines.append("")
    
    # Composed from (allOf)
    if 'allOf' in schema:
        md_lines.append("## Composed from")
        for item in schema['allOf']:
            if isinstance(item, dict) and '$ref' in item:
                ref_name = extract_file_name_wo_extension(item['$ref'])
                ref_relative_path = extract_ref_relative_path(item['$ref'])
                md_relative_path = convert_extension_from_schema_path_to_md(ref_relative_path)
                md_lines.append(f"- [{ref_name}]({md_relative_path})")
        md_lines.append("")
    
    # Properties
    if 'properties' in schema:
        md_lines.append("## Properties")
        md_lines.append("")
        md_lines.append("| PropertyName | Type | Required |")
        md_lines.append("|-------------|------|----------|")
        
        for prop_name, prop_data in schema['properties'].items():
            # プロパティの型情報を取得
            prop_type = get_property_type(prop_data)
            required = is_required_property(prop_name, schema)
            
            # 型情報と説明を同じセルに表示
            if 'description' in prop_data:
                prop_type = f"{prop_data['description']} <br> {prop_type}"
            md_lines.append(f"| {prop_name} | {prop_type} | {required} |")
    
    return "\n".join(md_lines)

def generate_output_path(schema_id: str) -> str:
    """
    スキーマIDから出力先のMarkdownファイルパスを生成する
    例: "https://jocf.startupstandard.org/jocf/main/schema/files/StockClassesFile.schema.json"
    → "docs/schema_markdown/files/StockClassesFile.md"
    """
    if not schema_id:
        raise ValueError("スキーマIDが指定されていません")
        
    # スキーマIDからベースURLを除去して相対パスを取得
    relative_path = schema_id[len(schema_config.SCHEMA_BASE_URL + '/'):]
    
    # .schema.jsonを.mdに置換
    md_path = relative_path.replace(schema_config.SCHEMA_FILE_EXTENSION, '.md')
    
    # 最終的な出力パスを生成
    return os.path.join(schema_config.MD_ROOT_RELATIVE_PATH, md_path)

def generate(input_file_path: str) -> None:
    """
    JSONスキーマファイルからMarkdownドキュメントを生成する

    Args:
        input_file_path: JSONスキーマファイルへのパス
    """
    # 入力ファイルの存在確認
    if not os.path.exists(input_file_path):
        print(f"エラー: 入力ファイル '{input_file_path}' が存在しません", file=sys.stderr)
        sys.exit(1)
    
    # JSONスキーマの読み込み
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        print(f"エラー: JSONの解析に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)
    
    # スキーマの妥当性チェック
    if not validate_json_schema(schema):
        print("エラー: 無効なJSONスキーマです。必須フィールド(title, properties)が不足しています", file=sys.stderr)
        sys.exit(1)
    
    # Markdownの生成
    markdown_content = generate_markdown(schema)
    
    # スキーマIDから出力パスを生成
    try:
        output_path = generate_output_path(schema['$id'])
    except (KeyError, ValueError) as e:
        print(f"エラー: 出力パスの生成に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 出力ディレクトリの作成（必要な場合）
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Markdownファイルの出力
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    except IOError as e:
        print(f"エラー: Markdownファイルの書き込みに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Convert JSON Schema to Markdown documentation',
        epilog='出力パスはスキーマの$idから自動的に生成されます'
    )
    parser.add_argument('input_file_path', help='JSONスキーマファイルへのパス')
    
    if len(sys.argv) > 2:
        parser.error('出力パスは指定不要です。スキーマの$idから自動的に生成されます。')
    
    args = parser.parse_args()
    generate(args.input_file_path)

if __name__ == "__main__":
    main()