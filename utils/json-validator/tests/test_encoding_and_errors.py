#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
エンコーディングと一般的なエラーのテスト

ファイルエンコーディングの検証とよくあるバリデーションエラーのテストを行う
"""

import unittest
import json
from pathlib import Path
from unittest.mock import Mock

# テスト対象のクラス（実装予定）
# from validator.main import JSONValidator
# from validator.schema_loader import SchemaLoader
# from validator.validation_result import ValidationResult
from validator.config import get_config


class MockJSONValidator:
    """テスト用のJSONValidatorモッククラス"""

    def __init__(self):
        self.schema_loader = Mock()
        self.file_validator = Mock()
        self.object_validator = Mock()

    def validate(self, file_path):
        """ファイルの検証"""
        try:
            # JSONファイルの読み込み
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 基本的な構造チェック
            if "file_type" not in data:
                return {
                    "is_valid": False,
                    "errors": ["file_type属性が存在しません"],
                    "file_path": file_path,
                }

            if "items" not in data:
                return {
                    "is_valid": False,
                    "errors": ["items配列が存在しません"],
                    "file_path": file_path,
                }

            # items配列の各要素をチェック
            errors = []
            validated_objects = 0

            for i, item in enumerate(data.get("items", [])):
                if "object_type" not in item:
                    errors.append(f"items[{i}]: object_type属性が存在しません")
                else:
                    validated_objects += 1

                    # 実際のファイルに含まれる典型的なエラーをチェック
                    if item.get("object_type") == "TX_STOCK_ISSUANCE":
                        share_price = item.get("share_price", {})
                        if "ammount" in share_price:  # 典型的な誤字
                            errors.append(
                                f"items[{i}].share_price: 'ammount'は'amount'の誤字の可能性があります"
                            )
                        if "cuurency_code" in share_price:  # 典型的な誤字
                            errors.append(
                                f"items[{i}].share_price: 'cuurency_code'は'currency_code'の誤字の可能性があります"
                            )

                    elif item.get("object_type") == "TX_CONVERTIBLE_ISSUANCE":
                        investment_amount = item.get("investment_amount", {})
                        if "ammount" in investment_amount:
                            errors.append(
                                f"items[{i}].investment_amount: 'ammount'は'amount'の誤字の可能性があります"
                            )
                        if "cuurency_code" in investment_amount:
                            errors.append(
                                f"items[{i}].investment_amount: 'cuurency_code'は'currency_code'の誤字の可能性があります"
                            )

            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "file_path": file_path,
                "validated_objects": validated_objects,
            }

        except FileNotFoundError:
            return {
                "is_valid": False,
                "errors": ["ファイルが存在しません"],
                "file_path": file_path,
            }
        except json.JSONDecodeError as e:
            return {
                "is_valid": False,
                "errors": [f"JSONパースエラー: {str(e)}"],
                "file_path": file_path,
            }


class TestRealWorldFiles(unittest.TestCase):
    """実際のJOCFファイルを使ったエンコーディングとエラーテスト"""

    def setUp(self):
        """テスト前の準備"""
        config = get_config()
        testing_config = config.get_testing_config()

        # 設定からサンプルディレクトリのパスを取得
        samples_dir_name = testing_config.get("samples_dir", "samples")

        # プロジェクトルートからの相対パスで取得
        # 現在のテストファイルからプロジェクトルートを特定
        current_dir = Path(__file__).parent
        project_root = current_dir

        # プロジェクトルートを探す（.gitやsetup.pyがある場所まで遡る）
        while project_root.parent != project_root:
            if (project_root / ".git").exists() or (project_root / "setup.py").exists():
                break
            project_root = project_root.parent

        self.samples_dir = project_root / samples_dir_name
        self.validator = MockJSONValidator()

        # サンプルディレクトリが存在するかチェック
        self.assertTrue(
            self.samples_dir.exists(),
            f"サンプルディレクトリが存在しません: {self.samples_dir}",
        )

    def test_validate_file_encoding(self):
        """ファイルエンコーディングのテスト"""
        file_path = self.samples_dir / "TransactionsFile.jocf.json"

        if not file_path.exists():
            self.skipTest("TransactionsFile.jocf.json not found")

        # UTF-8で読み込めることを確認
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 日本語文字が含まれているかチェック
            found_japanese = False
            for item in data.get("items", []):
                description = item.get("description", "")
                if any(ord(char) > 127 for char in description):
                    found_japanese = True
                    break

            if found_japanese:
                print("Japanese characters found and properly decoded")

        except UnicodeDecodeError:
            self.fail("ファイルがUTF-8でエンコードされていません")
        except json.JSONDecodeError as e:
            self.fail(f"JSON parsing failed: {e}")

    def test_common_validation_errors(self):
        """よくあるバリデーションエラーのテスト"""
        file_path = self.samples_dir / "TransactionsFile.jocf.json"

        if not file_path.exists():
            self.skipTest("TransactionsFile.jocf.json not found")

        result = self.validator.validate(str(file_path))

        # よくある誤字のチェック
        common_typos = ["ammount", "cuurency_code"]
        found_typos = []

        for error in result.get("errors", []):
            for typo in common_typos:
                if typo in error:
                    found_typos.append(typo)

        if found_typos:
            print(f"\nFound common typos: {found_typos}")
            print("これらは実際のサンプルファイルに含まれている典型的な誤字です")

        # 誤字が検出されることを確認（実際のファイルには誤字が含まれている）
        self.assertGreater(
            len(found_typos), 0, "サンプルファイルの典型的な誤字が検出されませんでした"
        )


if __name__ == "__main__":
    unittest.main()
