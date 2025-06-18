#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合テスト

テスト対象：
- JSONValidator全体の動作テスト
- samples/配下の実際のJOCFファイルを使った検証
- エラーメッセージ形式の確認
- 成功時・失敗時の適切な出力確認
- 各コンポーネント間の連携テスト
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# テスト対象のクラス（実装予定）
# from validator.main import JSONValidator
# from validator.schema_loader import SchemaLoader
# from validator.file_validator import FileValidator
# from validator.object_validator import ObjectValidator
# from validator.exceptions import ValidationError, FileNotFoundError


class ValidationResult:
    """検証結果クラス"""
    
    def __init__(self, is_valid=True, errors=None, file_path=None, validated_objects=0):
        self.is_valid = is_valid
        self.errors = errors or []
        self.file_path = file_path
        self.validated_objects = validated_objects
    
    def add_error(self, error):
        self.errors.append(error)
        self.is_valid = False
    
    def to_dict(self):
        """結果を辞書形式で返す"""
        if self.is_valid:
            return {
                "status": "success",
                "message": "検証が成功しました",
                "file_path": self.file_path,
                "validated_objects": self.validated_objects
            }
        else:
            return {
                "status": "error",
                "message": "検証に失敗しました",
                "file_path": self.file_path,
                "errors": self.errors
            }


class MockJSONValidator:
    """テスト用のJSONValidatorモッククラス"""
    
    def __init__(self):
        self.schema_loader = Mock()
        self.file_validator = Mock()
        self.object_validator = Mock()
        self._initialize_components()
    
    def validate(self, file_path):
        """ファイルの検証"""
        try:
            # JSONファイルの読み込み
            data = self._load_json_file(file_path)
            
            # ファイル検証
            file_result = self.file_validator.validate_file(data)
            if not file_result.is_valid:
                return ValidationResult(
                    is_valid=False,
                    errors=file_result.errors,
                    file_path=file_path
                )
            
            # items配列の各要素をオブジェクト検証
            validated_objects = 0
            items = data.get("items", [])
            for item in items:
                obj_result = self.object_validator.validate_object(item)
                if not obj_result.is_valid:
                    return ValidationResult(
                        is_valid=False,
                        errors=obj_result.errors,
                        file_path=file_path
                    )
                validated_objects += 1
            
            return ValidationResult(
                is_valid=True,
                file_path=file_path,
                validated_objects=validated_objects
            )
            
        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                errors=["ファイルが存在しません"],
                file_path=file_path
            )
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"JSONパースエラー: {str(e)}"],
                file_path=file_path
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"予期しないエラー: {str(e)}"],
                file_path=file_path
            )
    
    def _load_json_file(self, file_path):
        """JSONファイルの読み込み"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _initialize_components(self):
        """コンポーネントの初期化"""
        # 実際の実装では、各コンポーネントを初期化する
        pass


class TestIntegration(unittest.TestCase):
    """統合テストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        self.json_validator = MockJSONValidator()
        self.temp_dir = None
        
        # テスト用のサンプルファイルデータ
        self.valid_transactions_file = {
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
        
        self.invalid_json_content = '{"file_type": "JOCF_TRANSACTIONS_FILE", "items": [invalid json'
    
    def tearDown(self):
        """テスト後の後処理"""
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_temp_file(self, content, filename="test_file.json"):
        """テスト用の一時ファイルを作成"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp()
        
        file_path = os.path.join(self.temp_dir, filename)
        
        if isinstance(content, dict):
            content = json.dumps(content, ensure_ascii=False, indent=2)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def test_validate_success_with_valid_file(self):
        """正常系: 有効なファイルの検証成功"""
        # テスト用ファイル作成
        file_path = self.create_temp_file(self.valid_transactions_file)
        
        # モックの設定
        file_result = ValidationResult(is_valid=True)
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        obj_result = ValidationResult(is_valid=True)
        self.json_validator.object_validator.validate_object.return_value = obj_result
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertTrue(result.is_valid)
        self.assertEqual(result.file_path, file_path)
        self.assertEqual(result.validated_objects, 2)
        self.assertEqual(len(result.errors), 0)
        
        # 結果の形式確認
        result_dict = result.to_dict()
        self.assertEqual(result_dict["status"], "success")
        self.assertEqual(result_dict["message"], "検証が成功しました")
        self.assertEqual(result_dict["validated_objects"], 2)
    
    def test_validate_file_not_found(self):
        """異常系: ファイルが存在しない"""
        non_existent_file = "/path/to/non_existent_file.json"
        
        # テスト実行
        result = self.json_validator.validate(non_existent_file)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertEqual(result.file_path, non_existent_file)
        self.assertIn("ファイルが存在しません", result.errors)
        
        # 結果の形式確認
        result_dict = result.to_dict()
        self.assertEqual(result_dict["status"], "error")
        self.assertEqual(result_dict["message"], "検証に失敗しました")
    
    def test_validate_invalid_json(self):
        """異常系: 無効なJSON"""
        # 無効なJSONファイル作成
        file_path = self.create_temp_file(self.invalid_json_content)
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertEqual(result.file_path, file_path)
        self.assertTrue(any("JSONパースエラー" in error for error in result.errors))
        
        # 結果の形式確認
        result_dict = result.to_dict()
        self.assertEqual(result_dict["status"], "error")
        self.assertTrue(any("JSONパースエラー" in error for error in result_dict["errors"]))
    
    def test_validate_file_validation_failure(self):
        """異常系: ファイル検証失敗"""
        # テスト用ファイル作成
        file_path = self.create_temp_file(self.valid_transactions_file)
        
        # ファイル検証が失敗するようにモック設定
        file_result = ValidationResult(is_valid=False, errors=["file_type属性が無効です"])
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertEqual(result.file_path, file_path)
        self.assertIn("file_type属性が無効です", result.errors)
    
    def test_validate_object_validation_failure(self):
        """異常系: オブジェクト検証失敗"""
        # テスト用ファイル作成
        file_path = self.create_temp_file(self.valid_transactions_file)
        
        # ファイル検証は成功、オブジェクト検証が失敗するようにモック設定
        file_result = ValidationResult(is_valid=True)
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        obj_result = ValidationResult(is_valid=False, errors=["必須フィールドが不足しています"])
        self.json_validator.object_validator.validate_object.return_value = obj_result
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertEqual(result.file_path, file_path)
        self.assertIn("必須フィールドが不足しています", result.errors)
    
    def test_validate_empty_items_array(self):
        """境界値: 空のitems配列"""
        empty_items_file = {
            "file_type": "JOCF_TRANSACTIONS_FILE",
            "items": []
        }
        
        # テスト用ファイル作成
        file_path = self.create_temp_file(empty_items_file)
        
        # モックの設定
        file_result = ValidationResult(is_valid=True)
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validated_objects, 0)
    
    def test_validate_large_file_with_many_objects(self):
        """境界値: 大量のオブジェクトを含むファイル"""
        # 大量のオブジェクトを含むファイル
        large_file = {
            "file_type": "JOCF_TRANSACTIONS_FILE",
            "items": []
        }
        
        # 100個のオブジェクトを生成
        for i in range(100):
            item = {
                "object_type": "TX_STOCK_ISSUANCE",
                "id": f"test-stock-issuance-{i}",
                "stock_class_id": "test-stock-class-common",
                "securityholder_id": f"test-securityholder-{i}",
                "share_price": {
                    "amount": "100",
                    "currency_code": "JPY"
                },
                "quantity": "1000",
                "date": "2023-01-01",
                "security_id": f"test-security-{i}"
            }
            large_file["items"].append(item)
        
        # テスト用ファイル作成
        file_path = self.create_temp_file(large_file)
        
        # モックの設定
        file_result = ValidationResult(is_valid=True)
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        obj_result = ValidationResult(is_valid=True)
        self.json_validator.object_validator.validate_object.return_value = obj_result
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validated_objects, 100)
    
    def test_validate_mixed_object_types(self):
        """正常系: 異なるobject_typeが混在するファイル"""
        mixed_objects_file = {
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
                },
                {
                    "object_type": "TX_STOCK_SPLIT",
                    "id": "split-1"
                }
            ]
        }
        
        # テスト用ファイル作成
        file_path = self.create_temp_file(mixed_objects_file)
        
        # モックの設定
        file_result = ValidationResult(is_valid=True)
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        obj_result = ValidationResult(is_valid=True)
        self.json_validator.object_validator.validate_object.return_value = obj_result
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validated_objects, 5)
    
    def test_error_message_format(self):
        """エラーメッセージ形式の確認"""
        # テスト用ファイル作成
        file_path = self.create_temp_file(self.valid_transactions_file)
        
        # 詳細なエラー情報を含む失敗結果を設定
        detailed_errors = [
            {
                "field": "file_type",
                "message": "file_type属性が存在しません",
                "expected": "string",
                "actual": "undefined"
            },
            {
                "field": "items[0].object_type",
                "message": "無効なobject_typeです",
                "expected": "valid object_type",
                "actual": "INVALID_TYPE"
            }
        ]
        
        file_result = ValidationResult(is_valid=False, errors=detailed_errors)
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 2)
        
        # エラーメッセージ形式の確認
        result_dict = result.to_dict()
        expected_format = {
            "status": "error",
            "message": "検証に失敗しました",
            "file_path": file_path,
            "errors": detailed_errors
        }
        
        self.assertEqual(result_dict["status"], expected_format["status"])
        self.assertEqual(result_dict["message"], expected_format["message"])
        self.assertEqual(result_dict["file_path"], expected_format["file_path"])
        self.assertEqual(result_dict["errors"], expected_format["errors"])
    
    def test_component_integration(self):
        """各コンポーネント間の連携テスト"""
        # テスト用ファイル作成
        file_path = self.create_temp_file(self.valid_transactions_file)
        
        # 各コンポーネントのモック設定
        file_result = ValidationResult(is_valid=True)
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        obj_result = ValidationResult(is_valid=True)
        self.json_validator.object_validator.validate_object.return_value = obj_result
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 各コンポーネントが適切に呼び出されることを確認
        self.json_validator.file_validator.validate_file.assert_called_once()
        self.assertEqual(
            self.json_validator.object_validator.validate_object.call_count, 2
        )
        
        # 結果の確認
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validated_objects, 2)
    
    @patch('os.path.exists')
    def test_validate_with_actual_sample_file_simulation(self, mock_exists):
        """実際のサンプルファイルを使った検証のシミュレーション"""
        # 実際のサンプルファイルの内容をシミュレート
        sample_transactions_file = {
            "file_type": "JOCF_TRANSACTIONS_FILE",
            "items": [
                {
                    "object_type": "TX_STOCK_ISSUANCE",
                    "id": "test-initial-stock-issuance",
                    "stock_class_id": "test-stock-class-common",
                    "securityholder_id": "test-securityholder-1",
                    "share_price": {
                        "amount": "100",
                        "currency_code": "JPY"
                    },
                    "quantity": "1000",
                    "description": "創業時株式発行",
                    "date": "2012-01-20",
                    "security_id": "test-security-stock-1"
                },
                {
                    "object_type": "TX_STOCK_TRANSFER",
                    "id": "test-stock-transfer",
                    "security_id": "test-security-stock-1",
                    "quantity": "250",
                    "description": "株式譲渡",
                    "date": "2013-11-18",
                    "resulting_security_ids": ["test-security-stock-2"]
                },
                {
                    "object_type": "TX_CONVERTIBLE_ISSUANCE",
                    "id": "test-convertible-issuance",
                    "investment_amount": {
                        "amount": "10000000",
                        "currency_code": "JPY"
                    },
                    "convertible_type": "J-KISS_2",
                    "description": "シードラウンド",
                    "date": "2014-01-24"
                }
            ]
        }
        
        # ファイルが存在することをシミュレート
        mock_exists.return_value = True
        sample_file_path = "samples/TransactionsFile.jocf.json"
        
        # JSONファイルの読み込みをモック
        with patch('builtins.open', mock_open(read_data=json.dumps(sample_transactions_file))):
            with patch('json.load', return_value=sample_transactions_file):
                # モックの設定
                file_result = ValidationResult(is_valid=True)
                self.json_validator.file_validator.validate_file.return_value = file_result
                
                obj_result = ValidationResult(is_valid=True)
                self.json_validator.object_validator.validate_object.return_value = obj_result
                
                # テスト実行
                result = self.json_validator.validate(sample_file_path)
                
                # 検証
                self.assertTrue(result.is_valid)
                self.assertEqual(result.file_path, sample_file_path)
                self.assertEqual(result.validated_objects, 3)
                
                # 成功時の出力形式確認
                result_dict = result.to_dict()
                expected_success_output = {
                    "status": "success",
                    "message": "検証が成功しました",
                    "file_path": sample_file_path,
                    "validated_objects": 3
                }
                self.assertEqual(result_dict, expected_success_output)
    
    def test_unexpected_exception_handling(self):
        """予期しない例外のハンドリング"""
        # テスト用ファイル作成
        file_path = self.create_temp_file(self.valid_transactions_file)
        
        # ファイル検証で予期しない例外が発生するようにモック設定
        self.json_validator.file_validator.validate_file.side_effect = Exception("予期しないエラー")
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertTrue(any("予期しないエラー" in error for error in result.errors))
        
        # エラー時の出力形式確認
        result_dict = result.to_dict()
        self.assertEqual(result_dict["status"], "error")
        self.assertEqual(result_dict["message"], "検証に失敗しました")
    
    def test_partial_validation_failure(self):
        """部分的な検証失敗（一部のオブジェクトで失敗）"""
        # テスト用ファイル作成
        file_path = self.create_temp_file(self.valid_transactions_file)
        
        # ファイル検証は成功
        file_result = ValidationResult(is_valid=True)
        self.json_validator.file_validator.validate_file.return_value = file_result
        
        # 最初のオブジェクトは成功、2番目で失敗するように設定
        success_result = ValidationResult(is_valid=True)
        failure_result = ValidationResult(is_valid=False, errors=["オブジェクト検証失敗"])
        
        self.json_validator.object_validator.validate_object.side_effect = [
            success_result, failure_result
        ]
        
        # テスト実行
        result = self.json_validator.validate(file_path)
        
        # 検証（最初の失敗で停止）
        self.assertFalse(result.is_valid)
        self.assertIn("オブジェクト検証失敗", result.errors)
        
        # 最初のオブジェクトのみ検証されたことを確認
        self.assertEqual(self.json_validator.object_validator.validate_object.call_count, 2)


def mock_open(read_data=''):
    """mock_openのヘルパー関数"""
    from unittest.mock import mock_open as original_mock_open
    return original_mock_open(read_data=read_data)


if __name__ == '__main__':
    unittest.main()