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
from validator.validation_result import ValidationResult, AggregatedValidationResult


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
        mock_schema_loader.get_registry.return_value = Mock()
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
                        "$ref": "https://test.example.com/test-schema.json"
                    }
                }
            },
            "required": ["file_type", "items"]
        }
        
        # ObjectValidatorのために必要なモック設定
        # Registryは実際のインスタンスを作成（Mockだと iteration エラーになる）
        from referencing import Registry
        from referencing.jsonschema import DRAFT202012
        
        registry = Registry()
        test_schema = {
            "$id": "https://test.example.com/test-schema.json",
            "type": "object",
            "properties": {
                "object_type": {"type": "string", "const": "TEST_OBJECT"},
                "id": {"type": "string"}
            },
            "required": ["object_type", "id"]
        }
        resource = DRAFT202012.create_resource(test_schema)
        registry = registry.with_resource("https://test.example.com/test-schema.json", resource)
        
        mock_schema_loader.get_registry.return_value = registry
        mock_schema_loader.get_object_schema.return_value = {
            "type": "object",
            "properties": {
                "object_type": {"type": "string", "const": "TEST_OBJECT"},
                "id": {"type": "string"}
            },
            "required": ["object_type", "id"]
        }
        
        # FileValidatorが使用するメソッドもモック
        from validator.types import FileType, ObjectType
        file_type = FileType("JOCF_TRANSACTIONS_FILE")
        object_type = ObjectType("TEST_OBJECT")
        mock_schema_loader.get_allowed_object_types.return_value = [object_type]
        mock_schema_loader.has_object_schema.return_value = True
        
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


class TestJSONValidatorValidateMultiple(unittest.TestCase):
    """validate_multipleメソッドテスト"""
    
    def setUp(self):
        self.validator = JSONValidator()
    
    def test_validate_multiple_empty_list(self):
        """validate_multiple: 空のリストでAggregatedValidationResultを返す"""
        # Given: 空のファイルパスリスト
        file_paths = []
        # When: 複数ファイル検証を実行
        result = self.validator.validate_multiple(file_paths)
        # Then: AggregatedValidationResultが返される
        self.assertIsInstance(result, AggregatedValidationResult)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.total_files, 0)
    
    def test_validate_multiple_single_file(self):
        """validate_multiple: 単一ファイルでAggregatedValidationResultを返す"""
        # Given: JSONファイル（内容は問わない）
        test_data = {"file_type": "JOCF_TRANSACTIONS_FILE", "items": []}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # When: 複数ファイル検証を実行（1ファイル）
            result = self.validator.validate_multiple([temp_path])
            # Then: AggregatedValidationResultが返される
            self.assertIsInstance(result, AggregatedValidationResult)
            self.assertEqual(result.total_files, 1)
            # 実際の検証結果は依存クラスの実装次第なので、構造のみテスト
        finally:
            os.unlink(temp_path)
    
    def test_validate_multiple_two_files(self):
        """validate_multiple: 複数ファイルで結果集約される"""
        # Given: 2つのJSONファイル
        data1 = {"file_type": "JOCF_TRANSACTIONS_FILE", "items": []}
        data2 = {"file_type": "JOCF_TRANSACTIONS_FILE", "items": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1:
            json.dump(data1, f1, ensure_ascii=False)
            path1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
            json.dump(data2, f2, ensure_ascii=False)
            path2 = f2.name
        
        try:
            # When: 複数ファイル検証を実行
            result = self.validator.validate_multiple([path1, path2])
            # Then: 結果が適切に集約される
            self.assertIsInstance(result, AggregatedValidationResult)
            self.assertEqual(result.total_files, 2)
            # 個別の検証結果は依存クラスの実装次第
        finally:
            os.unlink(path1)
            os.unlink(path2)
    
    def test_validate_multiple_with_detailed_validation_results(self):
        """validate_multiple: 詳細な検証結果の確認（実装済み依存クラス使用）"""
        # スキーマを事前読み込み
        self.validator.schema_loader.load_all_schemas()
        
        # Given: 有効ファイルと無効ファイル
        valid_data = {"file_type": "TransactionsFile", "items": []}
        invalid_data = {"file_type": "INVALID_FILE_TYPE", "items": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1:
            json.dump(valid_data, f1, ensure_ascii=False)
            valid_path = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
            json.dump(invalid_data, f2, ensure_ascii=False)
            invalid_path = f2.name
        
        try:
            # When: 複数ファイル検証を実行
            result = self.validator.validate_multiple([valid_path, invalid_path])
            
            # Then: 詳細な検証結果が確認される
            self.assertIsInstance(result, AggregatedValidationResult)
            self.assertEqual(result.total_files, 2)
            
            # 実装済み依存クラスの動作を期待
            # 少なくとも1つは無効になるはず（INVALID_FILE_TYPEのため）
            self.assertGreater(result.invalid_files, 0)
            self.assertFalse(result.is_valid)  # 1つでも無効なら全体無効
            
            # エラー詳細も確認
            all_errors = result.get_all_errors()
            self.assertGreater(len(all_errors), 0)
            
        finally:
            os.unlink(valid_path)
            os.unlink(invalid_path)
    
    def test_validate_multiple_non_existent_file_handling(self):
        """validate_multiple: 存在しないファイルの処理"""
        # Given: 存在するファイルと存在しないファイル
        valid_data = {"file_type": "TransactionsFile", "items": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_data, f, ensure_ascii=False)
            valid_path = f.name
        
        non_existent_path = "/path/to/non/existent/file.json"
        
        try:
            # When: 複数ファイル検証を実行
            result = self.validator.validate_multiple([valid_path, non_existent_path])
            
            # Then: エラーハンドリングされて結果に含まれる
            self.assertIsInstance(result, AggregatedValidationResult)
            self.assertEqual(result.total_files, 2)
            
            # 存在しないファイルは無効として扱われるはず
            self.assertGreater(result.invalid_files, 0)
            self.assertFalse(result.is_valid)
            
            # エラーメッセージにファイル関連のエラーが含まれるはず
            all_errors = result.get_all_errors()
            self.assertTrue(any("ファイル" in error for error in all_errors))
            
        finally:
            os.unlink(valid_path)


class TestJSONValidatorValidateDirectory(unittest.TestCase):
    """validate_directoryメソッドテスト"""
    
    def setUp(self):
        self.validator = JSONValidator()
    
    def test_validate_directory_empty_directory(self):
        """validate_directory: 空ディレクトリでAggregatedValidationResultを返す"""
        # Given: 空のディレクトリ
        with tempfile.TemporaryDirectory() as temp_dir:
            # When: ディレクトリ検証を実行
            result = self.validator.validate_directory(temp_dir)
            # Then: AggregatedValidationResultが返される
            self.assertIsInstance(result, AggregatedValidationResult)
            self.assertTrue(result.is_valid)
            self.assertEqual(result.total_files, 0)
    
    def test_validate_directory_with_json_files(self):
        """validate_directory: JSONファイルを含むディレクトリの検証"""
        # Given: JSONファイルを含むディレクトリ
        with tempfile.TemporaryDirectory() as temp_dir:
            # スキーマを事前読み込み
            self.validator.schema_loader.load_all_schemas()
            
            # テストファイルを作成
            file1_data = {"file_type": "TransactionsFile", "items": []}
            file2_data = {"file_type": "TransactionsFile", "items": []}
            
            file1_path = Path(temp_dir) / "test1.jocf.json"
            file2_path = Path(temp_dir) / "test2.jocf.json"
            
            with open(file1_path, 'w', encoding='utf-8') as f:
                json.dump(file1_data, f, ensure_ascii=False)
            with open(file2_path, 'w', encoding='utf-8') as f:
                json.dump(file2_data, f, ensure_ascii=False)
            
            # When: ディレクトリ検証を実行
            result = self.validator.validate_directory(temp_dir, "*.jocf.json")
            
            # Then: ファイルが検証されて結果が集約される
            self.assertIsInstance(result, AggregatedValidationResult)
            self.assertEqual(result.total_files, 2)
    
    def test_validate_directory_pattern_matching(self):
        """validate_directory: パターンマッチングの動作確認"""
        # Given: 異なる拡張子のファイルを含むディレクトリ
        with tempfile.TemporaryDirectory() as temp_dir:
            # JSONファイルとその他のファイルを作成
            json_data = {"file_type": "TransactionsFile", "items": []}
            
            json_path = Path(temp_dir) / "test.jocf.json"
            txt_path = Path(temp_dir) / "test.txt"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("This is not JSON")
            
            # When: JSONファイルのみをパターンで検証
            result = self.validator.validate_directory(temp_dir, "*.jocf.json")
            
            # Then: JSONファイルのみが対象となる
            self.assertIsInstance(result, AggregatedValidationResult)
            self.assertEqual(result.total_files, 1)
    
    def test_validate_directory_non_existent(self):
        """validate_directory: 存在しないディレクトリの処理"""
        # Given: 存在しないディレクトリパス
        non_existent_dir = "/path/to/non/existent/directory"
        
        # When: ディレクトリ検証を実行
        result = self.validator.validate_directory(non_existent_dir)
        
        # Then: エラーが適切に処理される
        self.assertIsInstance(result, AggregatedValidationResult)
        # 存在しないディレクトリはファイル数0として扱われるか、
        # またはエラーとして処理されるかは実装次第
        self.assertEqual(result.total_files, 0)
    
    def test_validate_directory_mixed_valid_invalid_files(self):
        """validate_directory: 有効・無効ファイル混在時の処理"""
        # Given: 有効・無効ファイルを含むディレクトリ
        with tempfile.TemporaryDirectory() as temp_dir:
            # スキーマを事前読み込み
            self.validator.schema_loader.load_all_schemas()
            
            valid_data = {"file_type": "TransactionsFile", "items": []}
            invalid_data = {"file_type": "INVALID_TYPE", "items": []}
            
            valid_path = Path(temp_dir) / "valid.jocf.json"
            invalid_path = Path(temp_dir) / "invalid.jocf.json"
            
            with open(valid_path, 'w', encoding='utf-8') as f:
                json.dump(valid_data, f, ensure_ascii=False)
            with open(invalid_path, 'w', encoding='utf-8') as f:
                json.dump(invalid_data, f, ensure_ascii=False)
            
            # When: ディレクトリ検証を実行
            result = self.validator.validate_directory(temp_dir, "*.jocf.json")
            
            # Then: 混在結果が適切に集約される
            self.assertIsInstance(result, AggregatedValidationResult)
            self.assertEqual(result.total_files, 2)
            self.assertGreater(result.invalid_files, 0)
            self.assertFalse(result.is_valid)


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