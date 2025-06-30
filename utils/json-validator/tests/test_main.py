#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSONValidator単体テスト

TDD原則に従ってJSONValidatorの各メソッドをテストします。
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# テスト対象
from validator.main import JSONValidator
from validator.exceptions import (
    JSONValidatorError, ConfigError, FileValidationError,
    ValidationError
)
from validator.validation_result import ValidationResult


class TestJSONValidatorInit(unittest.TestCase):
    """JSONValidator初期化テスト"""
    
    def test_init_with_default_config(self):
        """__init__: デフォルト設定での初期化"""
        # Given: デフォルト設定での初期化
        # When: JSONValidatorを作成
        validator = JSONValidator()
        # Then: 正常に初期化される
        self.assertIsNotNone(validator)
    
    def test_init_with_custom_config_path(self):
        """__init__: カスタム設定パスでの初期化"""
        # Given: 既存の設定ファイルパス
        config_path = "utils/json-validator/config/validator_config.json"
        # When: JSONValidatorを作成
        validator = JSONValidator(config_path=config_path)
        # Then: 正常に初期化される
        self.assertIsNotNone(validator)
    
    def test_init_stores_components(self):
        """__init__: 各コンポーネントが適切に初期化される"""
        # Given: デフォルト設定
        # When: JSONValidatorを作成
        validator = JSONValidator()
        # Then: 各コンポーネントが設定される
        self.assertIsNotNone(validator.config_manager)
        self.assertIsNotNone(validator.schema_loader)
        self.assertIsNotNone(validator.file_validator)
        # ObjectValidatorはFileValidatorが内部で持つため、直接アクセスしない


class TestJSONValidatorValidateFilePath(unittest.TestCase):
    """ファイルパス検証テスト"""
    
    def setUp(self):
        self.validator = JSONValidator()
    
    def test_validate_existing_file_path(self):
        """_validate_file_path: 存在するファイルパス"""
        # Given: 存在するファイル
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('{"test": "data"}')
            temp_path = f.name
        
        try:
            # When: ファイルパスを検証
            # Then: 例外が発生しない
            self.validator._validate_file_path(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_non_existent_file_path(self):
        """_validate_file_path: 存在しないファイルパス"""
        # Given: 存在しないファイルパス
        non_existent_path = "/path/to/non/existent/file.json"
        # When & Then: FileValidationErrorが発生
        with self.assertRaises(FileValidationError):
            self.validator._validate_file_path(non_existent_path)
    
    def test_validate_empty_file_path(self):
        """_validate_file_path: 空のファイルパス"""
        # Given: 空文字列
        empty_path = ""
        # When & Then: FileValidationErrorが発生
        with self.assertRaises(FileValidationError):
            self.validator._validate_file_path(empty_path)


class TestJSONValidatorLoadJsonFile(unittest.TestCase):
    """JSONファイル読み込みテスト"""
    
    def setUp(self):
        self.validator = JSONValidator()
    
    def test_load_valid_json_file(self):
        """_load_json_file: 有効なJSONファイル"""
        # Given: 有効なJSONファイル
        test_data = {"file_type": "JOCF_TRANSACTIONS_FILE", "items": []}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # When: JSONファイルを読み込み
            result = self.validator._load_json_file(temp_path)
            # Then: 正しいデータが返される
            self.assertEqual(result, test_data)
        finally:
            os.unlink(temp_path)
    
    def test_load_invalid_json_file(self):
        """_load_json_file: 無効なJSONファイル"""
        # Given: 無効なJSONファイル
        invalid_json = '{"file_type": "JOCF_TRANSACTIONS_FILE", "items": [invalid'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(invalid_json)
            temp_path = f.name
        
        try:
            # When & Then: FileValidationErrorが発生
            with self.assertRaises(FileValidationError):
                self.validator._load_json_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_non_existent_file(self):
        """_load_json_file: 存在しないファイル"""
        # Given: 存在しないファイルパス
        non_existent_path = "/path/to/non/existent/file.json"
        # When & Then: FileValidationErrorが発生
        with self.assertRaises(FileValidationError):
            self.validator._load_json_file(non_existent_path)


class TestJSONValidatorValidateMethod(unittest.TestCase):
    """validateメソッドテスト"""
    
    def setUp(self):
        self.validator = JSONValidator()
    
    @patch('validator.main.SchemaLoader')
    def test_validate_returns_validation_result(self, mock_schema_loader_class):
        """validate: ValidationResultを返す（統合テスト）"""
        # Given: モックされたSchemaLoader（最小限の有効なスキーマを返す）
        mock_schema_loader = Mock()
        mock_schema_loader.get_file_schema.return_value = {
            "type": "object",
            "properties": {
                "file_type": {"type": "string", "enum": ["JOCF_TRANSACTIONS_FILE"]},
                "items": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["file_type", "items"]
        }
        mock_schema_loader.get_ref_resolver.return_value = Mock()
        mock_schema_loader_class.return_value = mock_schema_loader
        
        # 有効なJSONファイル
        test_data = {"file_type": "JOCF_TRANSACTIONS_FILE", "items": []}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # When: ファイルを検証（実際のFileValidator/ObjectValidatorを使用）
            validator = JSONValidator()
            result = validator.validate(temp_path)
            # Then: ValidationResultが返される
            self.assertIsInstance(result, ValidationResult)
            self.assertTrue(result.is_valid)  # 実際の検証が成功することを確認
        finally:
            os.unlink(temp_path)
    
    def test_validate_with_invalid_file_type(self):
        """validate: 無効なfile_typeで失敗（統合テスト）"""
        # Given: 無効なfile_typeを持つJSONファイル（FileType enumに存在しない値）
        test_data = {"file_type": "COMPLETELY_INVALID_FILE_TYPE", "items": []}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # When: ファイルを検証（実際のFileValidatorを使用）
            validator = JSONValidator()
            result = validator.validate(temp_path)
            
            # Then: FileTypeのenum変換で失敗し、検証が失敗する
            self.assertFalse(result.is_valid)
            self.assertGreater(len(result.errors), 0)
            self.assertTrue(any("に対応するスキーマが見つかりません" in error for error in result.errors))
        finally:
            os.unlink(temp_path)
    
    @patch('validator.main.SchemaLoader')
    def test_validate_with_items_objects(self, mock_schema_loader_class):
        """validate: items配列にオブジェクトがある場合（統合テスト）"""
        # Given: モックされたSchemaLoader
        mock_schema_loader = Mock()
        mock_schema_loader.get_file_schema.return_value = {
            "type": "object",
            "properties": {
                "file_type": {"type": "string", "enum": ["JOCF_TRANSACTIONS_FILE"]},
                "items": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"$ref": "#/definitions/object1"},
                            {"$ref": "#/definitions/object2"}
                        ]
                    }
                }
            },
            "required": ["file_type", "items"]
        }
        
        # ObjectValidatorのために必要なモック設定
        mock_resolver = Mock()
        mock_resolver.resolve.return_value = (None, {
            "type": "object",
            "properties": {
                "object_type": {"type": "string", "const": "TEST_OBJECT"},
                "id": {"type": "string"}
            },
            "required": ["object_type", "id"]
        })
        mock_schema_loader.get_ref_resolver.return_value = mock_resolver
        mock_schema_loader.get_object_schema.return_value = {
            "type": "object",
            "properties": {
                "object_type": {"type": "string", "const": "TEST_OBJECT"},
                "id": {"type": "string"}
            },
            "required": ["object_type", "id"]
        }
        mock_schema_loader_class.return_value = mock_schema_loader
        
        # items配列にオブジェクトを含むJSONファイル
        test_data = {
            "file_type": "JOCF_TRANSACTIONS_FILE",
            "items": [
                {"object_type": "TEST_OBJECT", "id": "test-1"},
                {"object_type": "TEST_OBJECT", "id": "test-2"}
            ]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # When: ファイルを検証
            validator = JSONValidator()
            result = validator.validate(temp_path)
            
            # Then: 検証が成功する（実際のFileValidator/ObjectValidatorがitems配列を処理）
            self.assertTrue(result.is_valid)
        finally:
            os.unlink(temp_path)


class TestJSONValidatorStringMethods(unittest.TestCase):
    """文字列表現テスト"""
    
    def test_str_method(self):
        """__str__: 文字列表現を返す"""
        # Given: JSONValidator
        validator = JSONValidator()
        # When: 文字列に変換
        result = str(validator)
        # Then: 適切な文字列が返される
        self.assertIsInstance(result, str)
        self.assertIn("JSONValidator", result)
    
    def test_repr_method(self):
        """__repr__: デバッグ用文字列表現を返す"""
        # Given: JSONValidator
        validator = JSONValidator()
        # When: repr()を呼び出し
        result = repr(validator)
        # Then: 適切なデバッグ文字列が返される
        self.assertIsInstance(result, str)
        self.assertIn("JSONValidator", result)


if __name__ == '__main__':
    unittest.main()