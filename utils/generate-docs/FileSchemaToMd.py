#!/usr/bin/env python3

import argparse
import json
import os.path
import sys
from typing import Dict, Any

def validate_json_schema(schema: Dict[str, Any]) -> bool:
    """
    JSONスキーマの基本的な妥当性をチェックする
    """
    required_fields = ['title', 'properties']
    return all(field in schema for field in required_fields)

def extract_ref_name(ref_path: str) -> str:
    """
    $refパスから最後のファイル名部分を抽出する
    例: "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
    → "StockClass"
    """
    # パスの最後のファイル名を取得
    filename = ref_path.split('/')[-1]
    # .schema.jsonを除去
    return filename.replace('.schema.json', '')

def get_property_type(prop: Dict[str, Any]) -> str:
    """
    プロパティの型情報を取得する
    """
    if 'type' in prop:
        if prop['type'] == 'array' and 'items' in prop:
            items = prop['items']
            if 'oneOf' in items:
                # oneOfの場合は$refの値を列挙
                refs = []
                for item in items['oneOf']:
                    if '$ref' in item:
                        refs.append(extract_ref_name(item['$ref']))
                return "array of:\n" + "\n".join([f"- {ref}" for ref in refs])
            return f"array of {get_property_type(items)}"
        return prop['type']
    elif 'const' in prop:
        return f"const ({prop['const']})"
    return 'unknown'

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
                ref_name = extract_ref_name(item['$ref'])
                md_lines.append(f"- {ref_name}")
        md_lines.append("")
    
    # Properties
    if 'properties' in schema:
        md_lines.append("## Properties")
        md_lines.append("")
        md_lines.append("| PropertyName | Type | Required |")
        md_lines.append("|-------------|------|----------|")
        
        for prop_name, prop_data in schema['properties'].items():
            prop_type = get_property_type(prop_data)
            required = is_required_property(prop_name, schema)
            
            # 型情報に改行が含まれる場合（oneOfのリストなど）は、
            # 最初の行をテーブルセルに、残りを後続の行に配置
            type_lines = prop_type.split('\n')
            md_lines.append(f"| {prop_name} | {type_lines[0]} | {required} |")
            
            # 型情報の残りの行を出力
            if len(type_lines) > 1:
                for type_line in type_lines[1:]:
                    md_lines.append(f"|  | {type_line} |  |")
            
            # プロパティの説明があれば追加
            if 'description' in prop_data:
                md_lines.append(f"|  | {prop_data['description']} |  |")
    
    return "\n".join(md_lines)

def main():
    parser = argparse.ArgumentParser(description='Convert JSON Schema to Markdown documentation')
    parser.add_argument('input_file_path', help='Path to input JSON schema file')
    parser.add_argument('output_file_path', help='Path to output Markdown file')
    
    args = parser.parse_args()
    
    # 入力ファイルの存在確認
    if not os.path.exists(args.input_file_path):
        print(f"エラー: 入力ファイル '{args.input_file_path}' が存在しません", file=sys.stderr)
        sys.exit(1)
    
    # JSONスキーマの読み込み
    try:
        with open(args.input_file_path, 'r', encoding='utf-8') as f:
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
    
    # 出力ディレクトリの作成（必要な場合）
    output_dir = os.path.dirname(args.output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Markdownファイルの出力
    try:
        with open(args.output_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    except IOError as e:
        print(f"エラー: Markdownファイルの書き込みに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()