#!/usr/bin/env python3

import argparse
import json
import os.path
import sys
from typing import Dict, Any
import schema_config
from schema_to_md.property_util import get_property_type, get_property_description
from schema_to_md.schema_id_util import (
    extract_ref_relative_path,
    extract_file_name_wo_extension,
    convert_extension_from_schema_path_to_md,
    extract_ref_relative_path_to_root,
    generate_output_path,
)


def validate_json_schema(schema: Dict[str, Any]) -> bool:
    """
    JSONスキーマの基本的な妥当性をチェックする
    """
    required_fields = ["title", "$id"]
    return all(field in schema for field in required_fields)


def is_required_property(prop_name: str, schema: Dict[str, Any]) -> str:
    """
    プロパティが必須かどうかを判定する
    """
    required = schema.get("required", [])
    return "Yes" if prop_name in required else "No"


def generate_markdown(schema: Dict[str, Any]) -> str:
    """
    JSONスキーマからMarkdown形式のドキュメントを生成する
    """
    md_lines = []

    # Schema Name
    md_lines.append(f"# {schema.get('title', 'Untitled Schema')}")
    md_lines.append("")

    # Schema ID
    if "$id" in schema:
        md_lines.append(f"ID = `{schema['$id']}`")
        md_lines.append("")

    # インプットファイルの$idから、ルートディレクトリへの相対パスを取得
    input_file_relative_path_to_root = extract_ref_relative_path_to_root(schema["$id"])

    # Description
    description = schema.get("description")
    if description:
        md_lines.append("## Description")
        md_lines.append(description)
        md_lines.append("")

    # Type Information for Primitive Types
    if "type" in schema and not "properties" in schema:
        md_lines.append("## Type")
        type_info = [f"**Type**: {schema['type']}"]

        if "pattern" in schema:
            type_info.append(f"**Pattern**: `{schema['pattern']}`")
        if "format" in schema:
            type_info.append(f"**Format**: {schema['format']}")
        if "minimum" in schema:
            type_info.append(f"**Minimum**: {schema['minimum']}")
        if "maximum" in schema:
            type_info.append(f"**Maximum**: {schema['maximum']}")
        if "enum" in schema:
            type_info.append(
                f"**Allowed Values**: {', '.join(map(str, schema['enum']))}"
            )

        md_lines.extend(type_info)
        md_lines.append("")

    # Composed from (allOf)
    if "allOf" in schema:
        md_lines.append("## Composed from")
        for item in schema["allOf"]:
            if isinstance(item, dict) and "$ref" in item:
                ref_name = extract_file_name_wo_extension(item["$ref"])
                ref_relative_path = extract_ref_relative_path(item["$ref"])
                md_relative_path = convert_extension_from_schema_path_to_md(
                    ref_relative_path
                )
                md_lines.append(
                    f"- [{ref_name}]({input_file_relative_path_to_root}{md_relative_path})"
                )
        md_lines.append("")

    # Properties (for object types)
    if "properties" in schema:
        md_lines.append("## Properties")
        md_lines.append("")
        md_lines.append("| PropertyName | Type | Required | Description |")
        md_lines.append("|-------------|------|----------|-------------|")

        for prop_name, prop_data in schema["properties"].items():
            # プロパティの型情報と説明を取得
            prop_type = get_property_type(prop_data, input_file_relative_path_to_root)
            required = is_required_property(prop_name, schema)
            description = get_property_description(prop_data, schema)
            md_lines.append(
                f"| {prop_name} | {prop_type} | {required} | {description} |"
            )
            if prop_type == "object":
                # オブジェクト型の場合、子スキーマを再帰的に処理
                for sub_prop_name, sub_prop_data in prop_data["properties"].items():
                    sub_prop_type = get_property_type(
                        sub_prop_data, input_file_relative_path_to_root
                    )
                    # 子プロパティ情報の出力
                    sub_required = is_required_property(sub_prop_name, prop_data)
                    sub_description = get_property_description(sub_prop_data, prop_data)
                    md_lines.append(
                        f"| {prop_name}.{sub_prop_name} | {sub_prop_type} | {sub_required} | {sub_description} |"
                    )
                    if sub_prop_type == "object":
                        # さらにオブジェクト型の場合、孫スキーマを再帰的に処理
                        for sub_sub_prop_name, sub_sub_prop_data in sub_prop_data[
                            "properties"
                        ].items():
                            sub_sub_prop_type = get_property_type(
                                sub_sub_prop_data, input_file_relative_path_to_root
                            )
                            sub_sub_required = is_required_property(
                                sub_sub_prop_name, prop_data
                            )
                            sub_sub_description = get_property_description(
                                sub_sub_prop_data, prop_data
                            )
                            # 孫プロパティ情報の出力
                            md_lines.append(
                                f"| {prop_name}.{sub_prop_name}.{sub_sub_prop_name} | {sub_sub_prop_type} | {sub_sub_required} | {sub_sub_description} |"
                            )
            if prop_type == "array of object":
                # 配列の要素がオブジェクト型の場合、子スキーマを再帰的に処理
                for sub_prop_name, sub_prop_data in prop_data["items"][
                    "properties"
                ].items():
                    sub_prop_type = get_property_type(
                        sub_prop_data, input_file_relative_path_to_root
                    )
                    sub_required = is_required_property(sub_prop_name, prop_data)
                    sub_description = get_property_description(sub_prop_data, prop_data)
                    md_lines.append(
                        f"| {prop_name}.{sub_prop_name} | {sub_prop_type} | {sub_required} | {sub_description} |"
                    )
    return "\n".join(md_lines)


def generate(input_file_path: str) -> None:
    """
    JSONスキーマファイルからMarkdownドキュメントを生成する

    Args:
        input_file_path: JSONスキーマファイルへのパス
    """
    # 入力ファイルの存在確認
    if not os.path.exists(input_file_path):
        print(
            f"エラー: 入力ファイル '{input_file_path}' が存在しません", file=sys.stderr
        )
        sys.exit(1)

    # JSONスキーマの読み込み
    try:
        with open(input_file_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        print(f"エラー: JSONの解析に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    # スキーマの妥当性チェック
    if not validate_json_schema(schema):
        print(
            "エラー: 無効なJSONスキーマです。必須フィールド(title)が不足しています",
            file=sys.stderr,
        )
        sys.exit(1)

    # Markdownの生成
    markdown_content = generate_markdown(schema)

    # スキーマIDから出力パスを生成
    try:
        output_path = generate_output_path(schema["$id"])
    except (KeyError, ValueError) as e:
        print(f"エラー: 出力パスの生成に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    # 出力ディレクトリの作成（必要な場合）
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Markdownファイルの出力
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
    except IOError as e:
        print(f"エラー: Markdownファイルの書き込みに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSON Schema to Markdown documentation",
        epilog="出力パスはスキーマの$idから自動的に生成されます",
    )
    parser.add_argument("input_file_path", help="JSONスキーマファイルへのパス")

    if len(sys.argv) > 2:
        parser.error("出力パスは指定不要です。スキーマの$idから自動的に生成されます。")

    args = parser.parse_args()
    generate(args.input_file_path)


if __name__ == "__main__":
    main()
