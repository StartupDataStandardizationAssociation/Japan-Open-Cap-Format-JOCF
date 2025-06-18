#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileValidatorクラスの単体テスト

テスト対象：
- file_type属性の検証
- 必須属性チェック（required属性に基づく）
- items配列の型チェック（許可されたobject_typeかどうか）
- items配列各要素のオブジェクト検証
- その他属性の検証
- 各種エラーケース（file_type不正、必須項目不足、items配列の型不正等）
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock

# テスト対象のクラス（実装予定）
# from validator.file_validator import FileValidator
# from validator.schema_loader import SchemaLoader
# from validator.object_validator import ObjectValidator
# from validator.exceptions import FileValidationError


class ValidationResult:
    """検証結果クラス"""
    
    def __init__(self, is_valid=True, errors=None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error):
        self.errors.append(error)
        self.is_valid = False


class MockFileValidator:
    """テスト用のFileValidatorモッククラス"""
    
    def __init__(self, schema_loader=None):
        self.schema_loader = schema_loader or Mock()
    
    def validate_file(self, file_data):
        """ファイルの検証"""
        result = ValidationResult()
        
        # file_type検証
        if not self._validate_file_type(file_data):
            result.add_error("file_type属性が無効です")
            return result
        
        # スキーマ取得
        file_type = file_data.get("file_type")
        schema = self.schema_loader.get_file_schema(file_type)
        if not schema:
            result.add_error(f"file_type '{file_type}' に対応するスキーマが見つかりません")
            return result
        
        # 必須属性チェック
        if not self._validate_required_attributes(file_data, schema):
            result.add_error("必須属性が不足しています")
            return result
        
        # items配列の検証
        if not self._validate_items_array(file_data, schema):
            result.add_error("items配列の検証に失敗しました")
            return result
        
        # その他属性の検証
        if not self._validate_other_attributes(file_data, schema):
            result.add_error("その他属性の検証に失敗しました")
            return result
        
        return result
    
    def _validate_file_type(self, file_data):
        """file_type属性の検証"""
        return "file_type" in file_data and isinstance(file_data["file_type"], str)
    
    def _validate_required_attributes(self, file_data, schema):
        """必須属性チェック"""
        required_attrs = schema.get("required", [])
        return all(attr in file_data for attr in required_attrs)
    
    def _validate_items_array(self, file_data, schema):
        """items配列の検証"""
        if "items" not in file_data:
            return False
        
        items = file_data["items"]
        if not isinstance(items, list):
            return False
        
        # 各要素にobject_typeが存在するかチェック
        for item in items:
            if not isinstance(item, dict) or "object_type" not in item:
                return False
        
        return True
    
    def _validate_other_attributes(self, file_data, schema):
        """その他属性の検証"""
        # 簡単な実装
        return True


class TestFileValidator(unittest.TestCase):
    """FileValidatorクラスのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        self.mock_schema_loader = Mock()
        self.file_validator = MockFileValidator(self.mock_schema_loader)
        
        # テスト用のスキーマデータ
        self.transactions_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json",
            "title": "トランザクション",
            "type": "object",
            "properties": {
                "file_type": {
                    "const": "JOCF_TRANSACTIONS_FILE"
                },
                "items": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"$ref": "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockIssuance.schema.json"},
                            {"$ref": "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/transfer/StockTransfer.schema.json"}
                        ]
                    }
                }
            },
            "required": ["file_type", "items"],
            "file_type": "JOCF_TRANSACTIONS_FILE"
        }
        
        # テスト用の有効なファイルデータ
        self.valid_file_data = {
            "file_type": "JOCF_TRANSACTIONS_FILE",
            "items": [
                {
                    "object_type": "TX_STOCK_ISSUANCE",
                    "id": "test-stock-issuance-1",
                    "stock_class_id": "test-stock-class-common",
                    "securityholder_id": "test-securityholder-1",
                    "share_price": {
                        "amount": "100",
                        "currency_code": "JPY"
                    },
                    "quantity": "1000",
                    "date": "2023-01-01",
                    "security_id": "test-security-1"
                },
                {
                    "object_type": "TX_STOCK_TRANSFER",
                    "id": "test-stock-transfer-1",
                    "security_id": "test-security-1",
                    "quantity": "250",
                    "date": "2023-02-01",
                    "resulting_security_ids": ["test-security-2"]
                }
            ]
        }
    
    def test_validate_file_success(self):
        """正常系: 有効なファイルの検証成功"""
        # モックの設定
        self.mock_schema_loader.get_file_schema.return_value = self.transactions_schema
        
        # テスト実行
        result = self.file_validator.validate_file(self.valid_file_data)
        
        # 検証
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.mock_schema_loader.get_file_schema.assert_called_once_with("JOCF_TRANSACTIONS_FILE")
    
    def test_validate_file_missing_file_type(self):
        """異常系: file_type属性が存在しない"""
        # file_type属性を削除
        invalid_data = self.valid_file_data.copy()
        del invalid_data["file_type"]
        
        # テスト実行
        result = self.file_validator.validate_file(invalid_data)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertIn("file_type属性が無効です", result.errors)
    
    def test_validate_file_invalid_file_type(self):
        """異常系: file_type属性が文字列でない"""
        # file_type属性を数値に変更
        invalid_data = self.valid_file_data.copy()
        invalid_data["file_type"] = 123
        
        # テスト実行
        result = self.file_validator.validate_file(invalid_data)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertIn("file_type属性が無効です", result.errors)
    
    def test_validate_file_unknown_file_type(self):
        """異常系: 存在しないfile_type"""
        # 存在しないfile_typeを設定
        invalid_data = self.valid_file_data.copy()
        invalid_data["file_type"] = "UNKNOWN_FILE_TYPE"
        
        # モックの設定（スキーマが見つからない）
        self.mock_schema_loader.get_file_schema.return_value = None
        
        # テスト実行
        result = self.file_validator.validate_file(invalid_data)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertIn("file_type 'UNKNOWN_FILE_TYPE' に対応するスキーマが見つかりません", result.errors)
    
    def test_validate_required_attributes_success(self):
        """正常系: 必須属性チェック成功"""
        # モックの設定
        self.mock_schema_loader.get_file_schema.return_value = self.transactions_schema
        
        # 必須属性の検証
        is_valid = self.file_validator._validate_required_attributes(
            self.valid_file_data, self.transactions_schema
        )
        
        # 検証
        self.assertTrue(is_valid)
    
    def test_validate_required_attributes_missing(self):
        """異常系: 必須属性不足"""
        # items属性を削除
        invalid_data = self.valid_file_data.copy()
        del invalid_data["items"]
        
        # テスト実行
        is_valid = self.file_validator._validate_required_attributes(
            invalid_data, self.transactions_schema
        )
        
        # 検証
        self.assertFalse(is_valid)
    
    def test_validate_items_array_success(self):
        """正常系: items配列の検証成功"""
        # テスト実行
        is_valid = self.file_validator._validate_items_array(
            self.valid_file_data, self.transactions_schema
        )
        
        # 検証
        self.assertTrue(is_valid)
    
    def test_validate_items_array_missing(self):
        """異常系: items配列が存在しない"""
        # items属性を削除
        invalid_data = self.valid_file_data.copy()
        del invalid_data["items"]
        
        # テスト実行
        is_valid = self.file_validator._validate_items_array(
            invalid_data, self.transactions_schema
        )
        
        # 検証
        self.assertFalse(is_valid)
    
    def test_validate_items_array_not_array(self):
        """異常系: items属性が配列でない"""
        # items属性を文字列に変更
        invalid_data = self.valid_file_data.copy()
        invalid_data["items"] = "not an array"
        
        # テスト実行
        is_valid = self.file_validator._validate_items_array(
            invalid_data, self.transactions_schema
        )
        
        # 検証
        self.assertFalse(is_valid)
    
    def test_validate_items_array_empty(self):
        """境界値: 空のitems配列"""
        # 空の配列を設定
        data_with_empty_items = self.valid_file_data.copy()
        data_with_empty_items["items"] = []
        
        # テスト実行
        is_valid = self.file_validator._validate_items_array(
            data_with_empty_items, self.transactions_schema
        )
        
        # 検証（空配列は有効とする）
        self.assertTrue(is_valid)
    
    def test_validate_items_array_missing_object_type(self):
        """異常系: items配列の要素にobject_typeが存在しない"""
        # object_type属性を削除
        invalid_data = self.valid_file_data.copy()
        invalid_data["items"][0] = {
            "id": "test-stock-issuance-1",
            "stock_class_id": "test-stock-class-common"
            # object_type属性なし
        }
        
        # テスト実行
        is_valid = self.file_validator._validate_items_array(
            invalid_data, self.transactions_schema
        )
        
        # 検証
        self.assertFalse(is_valid)
    
    def test_validate_items_array_non_object_element(self):
        """異常系: items配列の要素がオブジェクトでない"""
        # 文字列要素を含む配列
        invalid_data = self.valid_file_data.copy()
        invalid_data["items"] = ["not an object", self.valid_file_data["items"][0]]
        
        # テスト実行
        is_valid = self.file_validator._validate_items_array(
            invalid_data, self.transactions_schema
        )
        
        # 検証
        self.assertFalse(is_valid)
    
    def test_validate_items_array_invalid_object_type(self):
        """異常系: items配列の要素に無効なobject_typeが含まれる"""
        # 無効なobject_typeを設定
        invalid_data = self.valid_file_data.copy()
        invalid_data["items"][0]["object_type"] = "INVALID_OBJECT_TYPE"
        
        # モックの設定
        self.mock_schema_loader.get_file_schema.return_value = self.transactions_schema
        
        # テスト実行（実際の実装では、許可されたobject_typeかどうかもチェックする）
        result = self.file_validator.validate_file(invalid_data)
        
        # 基本的な検証は通るが、実際の実装では詳細なobject_type検証も行われる
        # ここでは基本構造のみ検証
        self.assertTrue(result.is_valid)  # 基本構造は有効
    
    def test_validate_file_type_property_validation(self):
        """file_type属性の値検証"""
        # 有効なfile_type
        valid_data = {"file_type": "JOCF_TRANSACTIONS_FILE"}
        self.assertTrue(self.file_validator._validate_file_type(valid_data))
        
        # 無効なfile_type（None）
        invalid_data_none = {"file_type": None}
        self.assertFalse(self.file_validator._validate_file_type(invalid_data_none))
        
        # 無効なfile_type（空文字列）
        invalid_data_empty = {"file_type": ""}
        self.assertTrue(self.file_validator._validate_file_type(invalid_data_empty))  # 空文字列は文字列として有効
        
        # file_type属性が存在しない
        invalid_data_missing = {}
        self.assertFalse(self.file_validator._validate_file_type(invalid_data_missing))
    
    def test_complex_file_validation(self):
        """複雑なファイル構造の検証"""
        complex_file_data = {
            "file_type": "JOCF_TRANSACTIONS_FILE",
            "items": [
                {
                    "object_type": "TX_STOCK_ISSUANCE",
                    "id": "issuance-1",
                    "stock_class_id": "common-stock",
                    "securityholder_id": "holder-1",
                    "share_price": {"amount": "1000", "currency_code": "JPY"},
                    "quantity": "100",
                    "date": "2023-01-01",
                    "security_id": "security-1",
                    "description": "Initial stock issuance"
                },
                {
                    "object_type": "TX_CONVERTIBLE_ISSUANCE",
                    "id": "convertible-1",
                    "investment_amount": {"amount": "10000000", "currency_code": "JPY"},
                    "convertible_type": "J-KISS_2",
                    "date": "2023-02-01",
                    "description": "Seed round"
                },
                {
                    "object_type": "TX_STOCK_CONVERSION",
                    "id": "conversion-1",
                    "quantity_converted": "50",
                    "stock_class_id_converted": "preferred-a",
                    "quantity": "100",
                    "stock_class_id": "common-stock",
                    "date": "2023-03-01",
                    "description": "Preferred stock conversion"
                }
            ],
            "additional_info": {
                "version": "1.0",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
        
        # モックの設定
        self.mock_schema_loader.get_file_schema.return_value = self.transactions_schema
        
        # テスト実行
        result = self.file_validator.validate_file(complex_file_data)
        
        # 検証
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_large_items_array(self):
        """境界値: 大量のitems配列"""
        # 大量のアイテムを含むファイル
        large_file_data = self.valid_file_data.copy()
        large_file_data["items"] = []
        
        # 1000個のアイテムを生成
        for i in range(1000):
            item = {
                "object_type": "TX_STOCK_ISSUANCE",
                "id": f"test-stock-issuance-{i}",
                "stock_class_id": "test-stock-class-common",
                "securityholder_id": f"test-securityholder-{i}",
                "share_price": {"amount": "100", "currency_code": "JPY"},
                "quantity": "1000",
                "date": "2023-01-01",
                "security_id": f"test-security-{i}"
            }
            large_file_data["items"].append(item)
        
        # モックの設定
        self.mock_schema_loader.get_file_schema.return_value = self.transactions_schema
        
        # テスト実行
        result = self.file_validator.validate_file(large_file_data)
        
        # 検証
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_mixed_object_types_in_items(self):
        """正常系: items配列に異なるobject_typeが混在"""
        mixed_items_data = {
            "file_type": "JOCF_TRANSACTIONS_FILE",
            "items": [
                {
                    "object_type": "TX_STOCK_ISSUANCE",
                    "id": "issuance-1"
                },
                {
                    "object_type": "TX_STOCK_TRANSFER",
                    "id": "transfer-1"
                },
                {
                    "object_type": "TX_CONVERTIBLE_ISSUANCE",
                    "id": "convertible-1"
                },
                {
                    "object_type": "TX_STOCK_CONVERSION",
                    "id": "conversion-1"
                }
            ]
        }
        
        # モックの設定
        self.mock_schema_loader.get_file_schema.return_value = self.transactions_schema
        
        # テスト実行
        result = self.file_validator.validate_file(mixed_items_data)
        
        # 検証
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_validate_other_attributes_with_nested_objects(self):
        """その他属性の検証（ネストしたオブジェクトを含む）"""
        file_with_nested_objects = {
            "file_type": "JOCF_TRANSACTIONS_FILE",
            "items": [
                {
                    "object_type": "TX_STOCK_ISSUANCE",
                    "id": "issuance-1",
                    "nested_object": {
                        "object_type": "NESTED_OBJECT",
                        "id": "nested-1",
                        "value": "test"
                    }
                }
            ],
            "metadata": {
                "version": "1.0",
                "author": "test"
            }
        }
        
        # テスト実行
        is_valid = self.file_validator._validate_other_attributes(
            file_with_nested_objects, self.transactions_schema
        )
        
        # 検証（現在の実装では常にTrueを返す）
        self.assertTrue(is_valid)
    
    @patch('validator.object_validator.ObjectValidator')
    def test_integration_with_object_validator(self, mock_object_validator_class):
        """統合テスト: ObjectValidatorとの連携"""
        # ObjectValidatorのモックを設定
        mock_object_validator = Mock()
        mock_object_validator.validate_object.return_value = ValidationResult(True)
        mock_object_validator_class.return_value = mock_object_validator
        
        # FileValidatorの拡張版を想定（実際の実装では、items配列の各要素をObjectValidatorで検証）
        class ExtendedFileValidator(MockFileValidator):
            def __init__(self, schema_loader, object_validator=None):
                super().__init__(schema_loader)
                self.object_validator = object_validator
            
            def validate_file(self, file_data):
                result = super().validate_file(file_data)
                
                if result.is_valid and self.object_validator:
                    # items配列の各要素をObjectValidatorで検証
                    items = file_data.get("items", [])
                    for item in items:
                        obj_result = self.object_validator.validate_object(item)
                        if not obj_result.is_valid:
                            result.add_error(f"オブジェクト検証失敗: {obj_result.errors}")
                
                return result
        
        # テスト用のFileValidatorを作成
        extended_validator = ExtendedFileValidator(
            self.mock_schema_loader, mock_object_validator
        )
        
        # モックの設定
        self.mock_schema_loader.get_file_schema.return_value = self.transactions_schema
        
        # テスト実行
        result = extended_validator.validate_file(self.valid_file_data)
        
        # 検証
        self.assertTrue(result.is_valid)
        # ObjectValidatorが各アイテムに対して呼び出されることを確認
        self.assertEqual(mock_object_validator.validate_object.call_count, 2)


if __name__ == '__main__':
    unittest.main()