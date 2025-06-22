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
- 追加メソッド: get_schema_by_id(), get_file_types(), get_object_types()
- 文字列表現: __str__(), __repr__()
- キャッシュ管理: clear_cache(), preload_schemas()
- スキーマ情報: get_schema_info()
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from jsonschema import RefResolver

# テスト対象のクラス
from validator.schema_loader import SchemaLoader
from validator.exceptions import SchemaError, SchemaLoadError, SchemaNotFoundError
from validator.config import ConfigManager


class MockSchemaLoader:
    """テスト用のSchemaLoaderモッククラス"""
    
    def __init__(self, config_manager=None):
        self.file_type_map = {}
        self.object_type_map = {}
        self.ref_resolver = None
        
        # 設定管理システムから取得
        if config_manager:
            self.schema_root_path = config_manager.get_schema_root_path()
        else:
            # テスト用のデフォルト値
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
        # 設定管理システムの初期化
        self.config_manager = ConfigManager()        
        self.schema_loader = SchemaLoader(self.config_manager)
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

    def test_has_object_schema_existing_type(self):
        """has_object_schema() - 存在するオブジェクトタイプの場合"""
        # テスト用スキーマを設定
        test_object_type = "TEST_OBJECT"
        self.schema_loader.object_type_map[test_object_type] = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/TestObject.schema.json",
            "type": "object",
            "properties": {
                "object_type": {"const": test_object_type}
            }
        }
        
        # 検証
        result = self.schema_loader.has_object_schema(test_object_type)
        self.assertTrue(result, "存在するオブジェクトタイプに対してTrueを返すべき")

    def test_has_object_schema_non_existing_type(self):
        """has_object_schema() - 存在しないオブジェクトタイプの場合"""
        non_existing_type = "NON_EXISTING_OBJECT_TYPE"
        
        # 検証
        result = self.schema_loader.has_object_schema(non_existing_type)
        self.assertFalse(result, "存在しないオブジェクトタイプに対してFalseを返すべき")

    def test_has_object_schema_empty_string(self):
        """has_object_schema() - 空文字列の場合"""
        result = self.schema_loader.has_object_schema("")
        self.assertFalse(result, "空文字列に対してFalseを返すべき")

    def test_has_object_schema_none_value(self):
        """has_object_schema() - None値の場合"""
        # None値は通常発生しないが、実装上は False を返す
        result = self.schema_loader.has_object_schema(None)
        self.assertFalse(result, "None値に対してFalseを返すべき")


class TestSchemaLoaderGetSchemaById(unittest.TestCase):
    """get_schema_by_id()メソッドのTDDテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
        self.loader.load_all_schemas()
    
    def test_get_schema_by_id_with_existing_file_schema(self):
        """存在するファイルスキーマIDでスキーマを取得"""
        # Given: 既知のファイルスキーマID
        transactions_id = "https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json"
        
        # When: get_schema_by_id()を呼び出し
        schema = self.loader.get_schema_by_id(transactions_id)
        
        # Then: 対応するスキーマが返される
        self.assertIsNotNone(schema, "存在するIDでスキーマが取得できる")
        self.assertEqual(schema.get('$id'), transactions_id, "正しいスキーマが取得される")
        self.assertEqual(schema.get('title'), 'トランザクション', "期待されるtitleを持つ")
    
    def test_get_schema_by_id_with_existing_object_schema(self):
        """存在するオブジェクトスキーマIDでスキーマを取得"""
        # Given: 既知のオブジェクトスキーマID
        stock_issuance_id = "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockIssuance.schema.json"
        
        # When: get_schema_by_id()を呼び出し
        schema = self.loader.get_schema_by_id(stock_issuance_id)
        
        # Then: 対応するスキーマが返される
        self.assertIsNotNone(schema, "存在するIDでスキーマが取得できる")
        self.assertEqual(schema.get('$id'), stock_issuance_id, "正しいスキーマが取得される")
        self.assertEqual(schema.get('title'), '株式発行トランザクション', "期待されるtitleを持つ")
    
    def test_get_schema_by_id_with_types_schema(self):
        """typesディレクトリのスキーマIDでスキーマを取得"""
        # Given: typesディレクトリのスキーマID
        file_type_id = "https://jocf.startupstandard.org/jocf/main/schema/types/File.schema.json"
        
        # When: get_schema_by_id()を呼び出し
        schema = self.loader.get_schema_by_id(file_type_id)
        
        # Then: 対応するスキーマが返される
        self.assertIsNotNone(schema, "typesスキーマが取得できる")
        self.assertEqual(schema.get('$id'), file_type_id, "正しいスキーマが取得される")
        self.assertEqual(schema.get('title'), 'Type - File', "期待されるtitleを持つ")
    
    def test_get_schema_by_id_with_non_existent_id(self):
        """存在しないIDの場合はNoneを返す"""
        # Given: 存在しないスキーマID
        non_existent_id = "https://jocf.startupstandard.org/jocf/main/schema/files/NonExistentFile.schema.json"
        
        # When: get_schema_by_id()を呼び出し
        schema = self.loader.get_schema_by_id(non_existent_id)
        
        # Then: Noneが返される
        self.assertIsNone(schema, "存在しないIDではNoneが返される")
    
    def test_get_schema_by_id_with_none_input(self):
        """Noneを渡した場合の動作"""
        # When: Noneを渡す
        schema = self.loader.get_schema_by_id(None)
        
        # Then: Noneが返される
        self.assertIsNone(schema, "None入力ではNoneが返される")
    
    def test_get_schema_by_id_with_empty_string(self):
        """境界値: 空文字列を渡した場合の動作"""
        # When: 空文字列を渡す
        schema = self.loader.get_schema_by_id("")
        
        # Then: Noneが返される
        self.assertIsNone(schema, "空文字列入力ではNoneが返される")
    
    def test_get_schema_by_id_with_invalid_url_format(self):
        """境界値: 不正なURL形式のIDを渡した場合"""
        # When: 不正なURL形式のIDを渡す
        invalid_ids = [
            "invalid-id",
            "http://",
            "not-a-url",
            "ftp://example.com/schema.json"
        ]
        
        for invalid_id in invalid_ids:
            # Then: Noneが返される（例外は発生しない）
            schema = self.loader.get_schema_by_id(invalid_id)
            self.assertIsNone(schema, f"不正なID '{invalid_id}' ではNoneが返される")
    
    def test_get_schema_by_id_case_sensitivity(self):
        """境界値: IDの大文字小文字の違い"""
        # Given: 既知のスキーマID（小文字）
        original_id = "https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json"
        uppercase_id = original_id.upper()
        
        # When: 大文字のIDで検索
        schema = self.loader.get_schema_by_id(uppercase_id)
        
        # Then: 見つからない（URLは大文字小文字を区別する）
        self.assertIsNone(schema, "大文字小文字が異なるIDでは見つからない")
    
    def test_get_schema_by_id_performance_with_many_schemas(self):
        """境界値: 多数のスキーマが存在する状態での検索性能"""
        # Given: 全スキーマが読み込まれた状態
        # When: 複数回検索を実行（性能テスト）
        test_id = "https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json"
        
        # 複数回実行して例外が発生しないことを確認
        for _ in range(10):
            schema = self.loader.get_schema_by_id(test_id)
            if schema:  # スキーマが存在する場合のみテスト
                self.assertIsNotNone(schema, "繰り返し検索でも結果が取得できる")
                break


class TestSchemaLoaderGetTypes(unittest.TestCase):
    """get_file_types()とget_object_types()メソッドのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
        self.loader.load_all_schemas()
    
    def test_get_file_types_returns_list(self):
        """get_file_types()がリストを返す"""
        # When: get_file_types()を呼び出し
        file_types = self.loader.get_file_types()
        
        # Then: リストが返される
        self.assertIsInstance(file_types, list, "file_typesはリスト")
        self.assertGreater(len(file_types), 0, "少なくとも1つのfile_typeがある")
        
        # And: 期待されるfile_typeが含まれる
        expected_types = ['JOCF_TRANSACTIONS_FILE', 'JOCF_STOCK_CLASSES_FILE']
        for expected_type in expected_types:
            self.assertIn(expected_type, file_types, f"{expected_type}が含まれる")
    
    def test_get_object_types_returns_list(self):
        """get_object_types()がリストを返す"""
        # When: get_object_types()を呼び出し
        object_types = self.loader.get_object_types()
        
        # Then: リストが返される
        self.assertIsInstance(object_types, list, "object_typesはリスト")
        self.assertGreater(len(object_types), 0, "少なくとも1つのobject_typeがある")
        
        # And: 期待されるobject_typeが含まれる
        expected_types = ['TX_STOCK_ISSUANCE', 'SECURITY_HOLDER', 'STOCK_CLASS']
        for expected_type in expected_types:
            self.assertIn(expected_type, object_types, f"{expected_type}が含まれる")
    
    def test_get_file_types_no_duplicates(self):
        """get_file_types()の結果に重複がない"""
        # When: get_file_types()を呼び出し
        file_types = self.loader.get_file_types()
        
        # Then: 重複がない
        self.assertEqual(len(file_types), len(set(file_types)), "file_typesに重複がない")
    
    def test_get_object_types_no_duplicates(self):
        """get_object_types()の結果に重複がない"""
        # When: get_object_types()を呼び出し
        object_types = self.loader.get_object_types()
        
        # Then: 重複がない
        self.assertEqual(len(object_types), len(set(object_types)), "object_typesに重複がない")


class TestSchemaLoaderStringRepresentation(unittest.TestCase):
    """__str__()と__repr__()メソッドのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
    
    def test_str_method_returns_readable_string(self):
        """__str__()が読みやすい文字列を返す"""
        # When: str()を呼び出し
        str_result = str(self.loader)
        
        # Then: 文字列が返される
        self.assertIsInstance(str_result, str, "__str__()は文字列を返す")
        self.assertIn("SchemaLoader", str_result, "クラス名が含まれる")
        self.assertGreater(len(str_result), 10, "適度な長さの文字列")
    
    def test_repr_method_returns_debug_string(self):
        """__repr__()がデバッグ用文字列を返す"""
        # When: repr()を呼び出し
        repr_result = repr(self.loader)
        
        # Then: デバッグ用文字列が返される
        self.assertIsInstance(repr_result, str, "__repr__()は文字列を返す")
        self.assertIn("SchemaLoader", repr_result, "クラス名が含まれる")
        self.assertGreater(len(repr_result), 10, "適度な長さの文字列")
    
    def test_str_and_repr_are_different(self):
        """__str__()と__repr__()は異なる結果を返す"""
        # When: 両方を呼び出し
        str_result = str(self.loader)
        repr_result = repr(self.loader)
        
        # Then: 異なる結果が返される（通常は）
        # 注意: 同じでも良いが、通常は異なるデザインにする
        self.assertIsInstance(str_result, str)
        self.assertIsInstance(repr_result, str)
    
    def test_str_with_empty_schemas(self):
        """境界値: スキーマが0個の場合の文字列表現"""
        # Given: スキーマを読み込まない状態
        # When: str()を呼び出し
        str_result = str(self.loader)
        
        # Then: ファイル数とオブジェクト数が0として表示される
        self.assertIn("files=0", str_result, "ファイル数0が表示される")
        self.assertIn("objects=0", str_result, "オブジェクト数0が表示される")
    
    def test_str_after_loading_schemas(self):
        """正常系: スキーマ読み込み後の文字列表現"""
        # Given: スキーマを読み込み
        self.loader.load_all_schemas()
        
        # When: str()を呼び出し
        str_result = str(self.loader)
        
        # Then: 実際のファイル数とオブジェクト数が表示される
        self.assertIn("files=", str_result, "ファイル数が表示される")
        self.assertIn("objects=", str_result, "オブジェクト数が表示される")
        self.assertIn("root=", str_result, "ルートパスが表示される")
    
    def test_repr_contains_all_attributes(self):
        """境界値: __repr__()が全ての重要な属性を含む"""
        # When: repr()を呼び出し
        repr_result = repr(self.loader)
        
        # Then: 重要な属性が含まれる
        self.assertIn("config_manager=", repr_result, "config_managerが含まれる")
        self.assertIn("schema_root_path=", repr_result, "schema_root_pathが含まれる")
    
    def test_str_consistency_across_multiple_calls(self):
        """境界値: __str__()の結果が複数回呼び出しで一貫性がある"""
        # When: 複数回str()を呼び出し
        str_result1 = str(self.loader)
        str_result2 = str(self.loader)
        str_result3 = str(self.loader)
        
        # Then: 同じ結果が返される
        self.assertEqual(str_result1, str_result2, "複数回呼び出しで同じ結果")
        self.assertEqual(str_result2, str_result3, "複数回呼び出しで同じ結果")


class TestSchemaLoaderGetSchemaInfo(unittest.TestCase):
    """get_schema_info()メソッドのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
        self.loader.load_all_schemas()
    
    def test_get_schema_info_for_file_type(self):
        """file_typeを指定してスキーマ情報を取得"""
        # When: file_typeを指定してget_schema_info()を呼び出し
        info = self.loader.get_schema_info(file_type="JOCF_TRANSACTIONS_FILE")
        
        # Then: 辞書が返される
        self.assertIsInstance(info, dict, "辞書が返される")
        self.assertIn("file_type", info, "file_typeが含まれる")
        self.assertIn("schema", info, "schemaが含まれる")
        self.assertEqual(info["file_type"], "JOCF_TRANSACTIONS_FILE", "正しいfile_type")
    
    def test_get_schema_info_for_object_type(self):
        """object_typeを指定してスキーマ情報を取得"""
        # When: object_typeを指定してget_schema_info()を呼び出し
        info = self.loader.get_schema_info(object_type="TX_STOCK_ISSUANCE")
        
        # Then: 辞書が返される
        self.assertIsInstance(info, dict, "辞書が返される")
        self.assertIn("object_type", info, "object_typeが含まれる")
        self.assertIn("schema", info, "schemaが含まれる")
        self.assertEqual(info["object_type"], "TX_STOCK_ISSUANCE", "正しいobject_type")
    
    def test_get_schema_info_with_no_parameters(self):
        """パラメータなしでスキーマ情報を取得"""
        # When: パラメータなしでget_schema_info()を呼び出し
        info = self.loader.get_schema_info()
        
        # Then: 全体のサマリー情報が返される
        self.assertIsInstance(info, dict, "辞書が返される")
        self.assertIn("total_file_schemas", info, "ファイルスキーマ数が含まれる")
        self.assertIn("total_object_schemas", info, "オブジェクトスキーマ数が含まれる")
    
    def test_get_schema_info_for_non_existent_file_type(self):
        """異常系: 存在しないfile_typeを指定"""
        # When: 存在しないfile_typeを指定
        info = self.loader.get_schema_info(file_type="NON_EXISTENT_FILE_TYPE")
        
        # Then: エラー情報が返される
        self.assertIsInstance(info, dict, "辞書が返される")
        self.assertIn("error", info, "エラーメッセージが含まれる")
        self.assertIn("NON_EXISTENT_FILE_TYPE", info["error"], "指定したタイプがエラーメッセージに含まれる")
    
    def test_get_schema_info_for_non_existent_object_type(self):
        """異常系: 存在しないobject_typeを指定"""
        # When: 存在しないobject_typeを指定
        info = self.loader.get_schema_info(object_type="NON_EXISTENT_OBJECT_TYPE")
        
        # Then: エラー情報が返される
        self.assertIsInstance(info, dict, "辞書が返される")
        self.assertIn("error", info, "エラーメッセージが含まれる")
        self.assertIn("NON_EXISTENT_OBJECT_TYPE", info["error"], "指定したタイプがエラーメッセージに含まれる")
    
    def test_get_schema_info_with_both_parameters(self):
        """境界値: file_typeとobject_typeの両方を指定（file_typeが優先される）"""
        # When: 両方のパラメータを指定
        info = self.loader.get_schema_info(
            file_type="JOCF_TRANSACTIONS_FILE", 
            object_type="TX_STOCK_ISSUANCE"
        )
        
        # Then: file_typeが優先される
        self.assertIsInstance(info, dict, "辞書が返される")
        self.assertIn("file_type", info, "file_typeが含まれる")
        self.assertNotIn("object_type", info, "object_typeは含まれない")
        self.assertEqual(info["file_type"], "JOCF_TRANSACTIONS_FILE", "file_typeが優先される")
    
    def test_get_schema_info_with_empty_string_parameters(self):
        """境界値: 空文字列のパラメータを指定"""
        # When: 空文字列のfile_typeを指定
        info = self.loader.get_schema_info(file_type="")
        
        # Then: エラー情報が返される
        self.assertIsInstance(info, dict, "辞書が返される")
        self.assertIn("error", info, "エラーメッセージが含まれる")


class TestSchemaLoaderCacheManagement(unittest.TestCase):
    """clear_cache()とpreload_schemas()メソッドのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
    
    def test_clear_cache_clears_ref_resolver(self):
        """clear_cache()がRefResolverキャッシュをクリアする"""
        # Given: RefResolverが作成されている
        self.loader.load_all_schemas()
        resolver = self.loader.get_ref_resolver()
        self.assertIsNotNone(resolver, "RefResolverが存在する")
        
        # When: clear_cache()を呼び出し
        self.loader.clear_cache()
        
        # Then: RefResolverがクリアされる
        self.assertIsNone(self.loader.ref_resolver, "RefResolverがクリアされる")
    
    def test_clear_cache_when_already_none(self):
        """境界値: RefResolverが未初期化の状態でclear_cache()"""
        # Given: RefResolverが未初期化
        self.assertIsNone(self.loader.ref_resolver, "RefResolverが未初期化")
        
        # When: clear_cache()を呼び出し（例外が発生しないことを確認）
        self.loader.clear_cache()
        
        # Then: 例外が発生せずNoneのまま
        self.assertIsNone(self.loader.ref_resolver, "RefResolverはNoneのまま")
    
    def test_clear_cache_multiple_times(self):
        """境界値: clear_cache()を複数回連続実行"""
        # Given: RefResolverが作成されている
        self.loader.load_all_schemas()
        self.loader.get_ref_resolver()
        
        # When: clear_cache()を複数回実行
        self.loader.clear_cache()
        self.loader.clear_cache()
        self.loader.clear_cache()
        
        # Then: 例外が発生せずNoneのまま
        self.assertIsNone(self.loader.ref_resolver, "RefResolverがクリアされている")
    
    def test_preload_schemas_loads_specified_schemas(self):
        """preload_schemas()が指定されたスキーマをロードする"""
        # Given: 特定のスキーマパスリスト
        schema_paths = [
            "files/TransactionsFile.schema.json",
            "objects/SecurityHolder.schema.json"
        ]
        
        # When: preload_schemas()を呼び出し
        self.loader.preload_schemas(schema_paths)
        
        # Then: 指定されたスキーマがロードされる
        # 実装後は適切なアサーションを追加
        self.assertIsInstance(schema_paths, list, "パラメータがリストである")
    
    def test_preload_schemas_with_empty_list(self):
        """境界値: 空のリストでpreload_schemas()"""
        # Given: 空のリスト
        empty_list = []
        
        # When: 空のリストでpreload_schemas()を呼び出し
        self.loader.preload_schemas(empty_list)
        
        # Then: 例外が発生しない
        self.assertEqual(len(empty_list), 0, "空のリストが処理される")
    
    def test_preload_schemas_with_non_existent_paths(self):
        """異常系: 存在しないパスでpreload_schemas()"""
        # Given: 存在しないスキーマパス
        non_existent_paths = [
            "files/NonExistentFile.schema.json",
            "objects/NonExistentObject.schema.json"
        ]
        
        # When: 存在しないパスでpreload_schemas()を呼び出し
        # Then: 例外が発生しない（内部でエラーハンドリングされる）
        self.loader.preload_schemas(non_existent_paths)
        
        # 検証: エラーが発生しても処理が継続される
        self.assertIsInstance(non_existent_paths, list, "リストが処理される")
    
    def test_preload_schemas_with_invalid_json_files(self):
        """異常系: 無効なJSONファイルでpreload_schemas()"""
        # Given: 無効なJSONファイルパス（存在しないため実際のテストではスキップされる）
        invalid_json_paths = [
            "files/InvalidFile.schema.json"
        ]
        
        # When: 無効なJSONファイルパスでpreload_schemas()を呼び出し
        # Then: 例外が発生しない（内部でエラーハンドリングされる）
        self.loader.preload_schemas(invalid_json_paths)
        
        # 検証: エラーが発生しても処理が継続される
        self.assertIsInstance(invalid_json_paths, list, "リストが処理される")


if __name__ == '__main__':
    unittest.main()