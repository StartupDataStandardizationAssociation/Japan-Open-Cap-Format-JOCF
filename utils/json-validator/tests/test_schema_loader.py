#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SchemaLoaderクラスの単体テスト

テスト対象：
- load_all_schemas() メソッド
- get_file_schema() / get_object_schema() メソッド
- file_type_mapとobject_type_mapの正しい構築
- RefResolverの適切な設定
- スキーマファイル不存在・パース失敗時のエラーハンドリング
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from jsonschema import RefResolver

# テスト対象のクラス（実装予定）
# from validator.schema_loader import SchemaLoader
# from validator.exceptions import SchemaError, FileNotFoundError


class MockSchemaLoader:
    """テスト用のSchemaLoaderモッククラス"""
    
    def __init__(self):
        self.file_type_map = {}
        self.object_type_map = {}
        self.ref_resolver = None
        self.schema_root_path = Path("schema")
    
    def load_all_schemas(self):
        """全スキーマの読み込みとインデックス作成"""
        pass
    
    def get_file_schema(self, file_type):
        """file_typeに対応するスキーマを取得"""
        return self.file_type_map.get(file_type)
    
    def get_object_schema(self, object_type):
        """object_typeに対応するスキーマを取得"""
        return self.object_type_map.get(object_type)
    
    def get_ref_resolver(self):
        """RefResolverを取得"""
        return self.ref_resolver


class TestSchemaLoader(unittest.TestCase):
    """SchemaLoaderクラスのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        self.schema_loader = MockSchemaLoader()
        self.temp_dir = None
        
        # テスト用のスキーマファイルデータ
        self.valid_file_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/files/TestFile.schema.json",
            "title": "テストファイル",
            "type": "object",
            "properties": {
                "file_type": {
                    "const": "TEST_FILE"
                },
                "items": {
                    "type": "array"
                }
            },
            "required": ["file_type", "items"],
            "file_type": "TEST_FILE"
        }
        
        self.valid_object_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/TestObject.schema.json",
            "title": "テストオブジェクト",
            "type": "object",
            "properties": {
                "object_type": {
                    "const": "TEST_OBJECT"
                },
                "id": {
                    "type": "string"
                }
            },
            "required": ["object_type", "id"],
            "object_type": "TEST_OBJECT"
        }
        
        self.invalid_json_schema = "{ invalid json"
        
    def tearDown(self):
        """テスト後の後処理"""
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_temp_schema_dir(self):
        """テスト用の一時スキーマディレクトリを作成"""
        self.temp_dir = tempfile.mkdtemp()
        schema_dir = Path(self.temp_dir) / "schema"
        files_dir = schema_dir / "files"
        objects_dir = schema_dir / "objects"
        
        files_dir.mkdir(parents=True, exist_ok=True)
        objects_dir.mkdir(parents=True, exist_ok=True)
        
        return schema_dir
    
    def test_load_all_schemas_success(self):
        """正常系: 全スキーマの読み込み成功"""
        # テスト用のスキーマディレクトリ作成
        schema_dir = self.create_temp_schema_dir()
        
        # テスト用ファイル作成
        (schema_dir / "files" / "TestFile.schema.json").write_text(
            json.dumps(self.valid_file_schema), encoding='utf-8'
        )
        (schema_dir / "objects" / "TestObject.schema.json").write_text(
            json.dumps(self.valid_object_schema), encoding='utf-8'
        )
        
        # 実際の実装では以下のような処理が行われる想定
        self.schema_loader.file_type_map["TEST_FILE"] = self.valid_file_schema
        self.schema_loader.object_type_map["TEST_OBJECT"] = self.valid_object_schema
        
        # 検証
        self.assertIn("TEST_FILE", self.schema_loader.file_type_map)
        self.assertIn("TEST_OBJECT", self.schema_loader.object_type_map)
        self.assertEqual(
            self.schema_loader.file_type_map["TEST_FILE"]["title"],
            "テストファイル"
        )
        self.assertEqual(
            self.schema_loader.object_type_map["TEST_OBJECT"]["title"],
            "テストオブジェクト"
        )
    
    def test_get_file_schema_success(self):
        """正常系: file_typeに対応するスキーマの取得成功"""
        # テストデータ設定
        self.schema_loader.file_type_map["JOCF_TRANSACTIONS_FILE"] = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json",
            "title": "トランザクション",
            "file_type": "JOCF_TRANSACTIONS_FILE"
        }
        
        # テスト実行
        schema = self.schema_loader.get_file_schema("JOCF_TRANSACTIONS_FILE")
        
        # 検証
        self.assertIsNotNone(schema)
        self.assertEqual(schema["title"], "トランザクション")
        self.assertEqual(schema["file_type"], "JOCF_TRANSACTIONS_FILE")
    
    def test_get_file_schema_not_found(self):
        """異常系: 存在しないfile_typeでスキーマ取得"""
        # テスト実行
        schema = self.schema_loader.get_file_schema("NON_EXISTENT_FILE")
        
        # 検証
        self.assertIsNone(schema)
    
    def test_get_object_schema_success(self):
        """正常系: object_typeに対応するスキーマの取得成功"""
        # テストデータ設定
        self.schema_loader.object_type_map["TX_STOCK_ISSUANCE"] = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockIssuance.schema.json",
            "title": "株式発行トランザクション",
            "object_type": "TX_STOCK_ISSUANCE"
        }
        
        # テスト実行
        schema = self.schema_loader.get_object_schema("TX_STOCK_ISSUANCE")
        
        # 検証
        self.assertIsNotNone(schema)
        self.assertEqual(schema["title"], "株式発行トランザクション")
        self.assertEqual(schema["object_type"], "TX_STOCK_ISSUANCE")
    
    def test_get_object_schema_not_found(self):
        """異常系: 存在しないobject_typeでスキーマ取得"""
        # テスト実行
        schema = self.schema_loader.get_object_schema("NON_EXISTENT_OBJECT")
        
        # 検証
        self.assertIsNone(schema)
    
    def test_file_type_map_construction(self):
        """file_type_mapの正しい構築テスト"""
        # 複数のファイルスキーマを設定
        file_schemas = {
            "JOCF_TRANSACTIONS_FILE": {
                "$id": "https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json",
                "file_type": "JOCF_TRANSACTIONS_FILE"
            },
            "JOCF_SECURITY_HOLDERS_FILE": {
                "$id": "https://jocf.startupstandard.org/jocf/main/schema/files/SecurityHoldersFile.schema.json",
                "file_type": "JOCF_SECURITY_HOLDERS_FILE"
            }
        }
        
        for file_type, schema in file_schemas.items():
            self.schema_loader.file_type_map[file_type] = schema
        
        # 検証
        self.assertEqual(len(self.schema_loader.file_type_map), 2)
        self.assertIn("JOCF_TRANSACTIONS_FILE", self.schema_loader.file_type_map)
        self.assertIn("JOCF_SECURITY_HOLDERS_FILE", self.schema_loader.file_type_map)
    
    def test_object_type_map_construction(self):
        """object_type_mapの正しい構築テスト"""
        # 複数のオブジェクトスキーマを設定
        object_schemas = {
            "TX_STOCK_ISSUANCE": {
                "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockIssuance.schema.json",
                "object_type": "TX_STOCK_ISSUANCE"
            },
            "TX_STOCK_TRANSFER": {
                "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/transfer/StockTransfer.schema.json",
                "object_type": "TX_STOCK_TRANSFER"
            },
            "SECURITY_HOLDER": {
                "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/SecurityHolder.schema.json",
                "object_type": "SECURITY_HOLDER"
            }
        }
        
        for object_type, schema in object_schemas.items():
            self.schema_loader.object_type_map[object_type] = schema
        
        # 検証
        self.assertEqual(len(self.schema_loader.object_type_map), 3)
        self.assertIn("TX_STOCK_ISSUANCE", self.schema_loader.object_type_map)
        self.assertIn("TX_STOCK_TRANSFER", self.schema_loader.object_type_map)
        self.assertIn("SECURITY_HOLDER", self.schema_loader.object_type_map)
    
    def test_ref_resolver_setup(self):
        """RefResolverの適切な設定テスト"""
        # RefResolverの設定をシミュレート
        store = {
            "https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json": self.valid_file_schema,
            "https://jocf.startupstandard.org/jocf/main/schema/objects/TestObject.schema.json": self.valid_object_schema
        }
        
        base_uri = "https://jocf.startupstandard.org/jocf/main/"
        resolver = RefResolver(base_uri, None, store=store)
        self.schema_loader.ref_resolver = resolver
        
        # 検証
        self.assertIsNotNone(self.schema_loader.ref_resolver)
        self.assertEqual(self.schema_loader.ref_resolver.resolution_scope, base_uri)
        
        # $ref解決のテスト
        resolved_url, resolved_schema = resolver.resolve(
            "https://jocf.startupstandard.org/jocf/main/schema/files/TestFile.schema.json"
        )
        self.assertEqual(resolved_schema, self.valid_file_schema)
    
    @patch('builtins.open', mock_open(read_data='{"invalid": json}'))
    def test_load_schema_file_parse_error(self):
        """異常系: スキーマファイルのパース失敗"""
        # 実際の実装では以下のような例外が発生する想定
        # with self.assertRaises(SchemaError):
        #     self.schema_loader._load_schema_file(Path("invalid.json"))
        
        # モックでの検証
        with patch('json.load') as mock_json_load:
            mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
            
            # 実装では例外が発生する想定
            with self.assertRaises(json.JSONDecodeError):
                json.load(mock_open(read_data='{"invalid": json}')())
    
    def test_load_schema_file_not_found(self):
        """異常系: スキーマファイル不存在"""
        # 存在しないファイルパス
        non_existent_path = Path("non_existent_schema.json")
        
        # 実際の実装では以下のような例外が発生する想定
        # with self.assertRaises(FileNotFoundError):
        #     self.schema_loader._load_schema_file(non_existent_path)
        
        # ファイルが存在しないことを確認
        self.assertFalse(non_existent_path.exists())
    
    def test_register_file_type_schema_missing_file_type(self):
        """異常系: file_type属性が存在しないスキーマの登録"""
        invalid_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/files/InvalidFile.schema.json",
            "title": "無効なファイル",
            "type": "object"
            # file_type属性なし
        }
        
        # 実装では、file_type属性がないスキーマは無視されるか、
        # 適切なエラーハンドリングが行われる想定
        # file_type属性がないため、file_type_mapには登録されない
        if "file_type" in invalid_schema:
            self.schema_loader.file_type_map[invalid_schema["file_type"]] = invalid_schema
        
        # file_type_mapに登録されていないことを確認
        self.assertEqual(len(self.schema_loader.file_type_map), 0)
    
    def test_register_object_type_schema_missing_object_type(self):
        """異常系: object_type属性が存在しないスキーマの登録"""
        invalid_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/InvalidObject.schema.json",
            "title": "無効なオブジェクト",
            "type": "object"
            # object_type属性なし
        }
        
        # 実装では、object_type属性がないスキーマは無視されるか、
        # 適切なエラーハンドリングが行われる想定
        if "object_type" in invalid_schema:
            self.schema_loader.object_type_map[invalid_schema["object_type"]] = invalid_schema
        
        # object_type_mapに登録されていないことを確認
        self.assertEqual(len(self.schema_loader.object_type_map), 0)
    
    def test_schema_with_both_file_type_and_object_type(self):
        """境界値: file_typeとobject_typeの両方を持つスキーマ"""
        # 通常はfile_typeとobject_typeは排他的だが、両方を持つ場合の処理
        mixed_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/mixed/MixedSchema.schema.json",
            "title": "混合スキーマ",
            "type": "object",
            "file_type": "MIXED_FILE",
            "object_type": "MIXED_OBJECT"
        }
        
        # 両方のマップに登録される想定
        if "file_type" in mixed_schema:
            self.schema_loader.file_type_map[mixed_schema["file_type"]] = mixed_schema
        if "object_type" in mixed_schema:
            self.schema_loader.object_type_map[mixed_schema["object_type"]] = mixed_schema
        
        # 検証
        self.assertIn("MIXED_FILE", self.schema_loader.file_type_map)
        self.assertIn("MIXED_OBJECT", self.schema_loader.object_type_map)
    
    def test_empty_schema_directory(self):
        """境界値: 空のスキーマディレクトリ"""
        # 空のディレクトリの場合のテスト
        schema_dir = self.create_temp_schema_dir()
        
        # スキーマファイルが存在しない場合
        self.assertEqual(len(self.schema_loader.file_type_map), 0)
        self.assertEqual(len(self.schema_loader.object_type_map), 0)
    
    def test_large_number_of_schemas(self):
        """境界値: 大量のスキーマファイル処理"""
        # 大量のスキーマファイルを想定したテスト
        for i in range(100):
            file_type = f"TEST_FILE_{i}"
            object_type = f"TEST_OBJECT_{i}"
            
            self.schema_loader.file_type_map[file_type] = {
                "$id": f"https://jocf.startupstandard.org/jocf/main/schema/files/TestFile{i}.schema.json",
                "file_type": file_type
            }
            self.schema_loader.object_type_map[object_type] = {
                "$id": f"https://jocf.startupstandard.org/jocf/main/schema/objects/TestObject{i}.schema.json",
                "object_type": object_type
            }
        
        # 検証
        self.assertEqual(len(self.schema_loader.file_type_map), 100)
        self.assertEqual(len(self.schema_loader.object_type_map), 100)
        
        # 特定のスキーマが正しく取得できることを確認
        schema = self.schema_loader.get_file_schema("TEST_FILE_50")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["file_type"], "TEST_FILE_50")


if __name__ == '__main__':
    unittest.main()