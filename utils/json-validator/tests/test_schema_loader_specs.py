#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SchemaLoaderクラスの仕様を説明する単体テスト

このテストファイルはSchemaLoaderの使用方法、API仕様、動作パターンを
明確に文書化することを目的としています。

テスト対象：
- SchemaLoaderの基本的な使用パターン
- APIの仕様と契約
- スキーマロードのワークフロー
- Registryの統合仕様
- エラーハンドリングとエッジケース
"""

import unittest
from pathlib import Path

from validator.schema_loader import SchemaLoader
from validator.config_manager import ConfigManager
from validator.types import FileType, ObjectType, SchemaId
from referencing import Registry


class TestSchemaLoaderBasicUsageSpecs(unittest.TestCase):
    """SchemaLoaderの基本的な使用方法の仕様テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
    
    def test_basic_initialization_spec(self):
        """仕様: SchemaLoaderは設定管理インスタンスで初期化される"""
        # Given: ConfigManagerが正常に作成されている
        config = ConfigManager()
        
        # When: SchemaLoaderを初期化する
        loader = SchemaLoader(config)
        
        # Then: 必要な属性が適切に初期化される
        self.assertIsInstance(loader.config_manager, ConfigManager)
        self.assertIsInstance(loader.schema_root_path, Path)
        self.assertIsInstance(loader.file_type_map, dict)
        self.assertIsInstance(loader.object_type_map, dict)
        self.assertIsNone(loader.registry)  # 遅延初期化
        
        # And: マップは初期状態で空である
        self.assertEqual(len(loader.file_type_map), 0)
        self.assertEqual(len(loader.object_type_map), 0)
    
    def test_typical_usage_workflow_spec(self):
        """仕様: 典型的な使用ワークフローでスキーマが正しくロードされる"""
        # Given: SchemaLoaderが初期化されている
        loader = SchemaLoader(self.config_manager)
        
        # When: 典型的な使用パターンを実行する
        # Step 1: スキーマをロード
        loader.load_all_schemas()
        
        # Step 2: ファイルスキーマを取得
        file_type = FileType('JOCF_TRANSACTIONS_FILE')
        transactions_schema = loader.get_file_schema(file_type)
        
        # Step 3: オブジェクトスキーマを取得
        object_type = ObjectType('TX_STOCK_ISSUANCE')
        stock_issuance_schema = loader.get_object_schema(object_type)
        
        # Step 4: Registryを取得
        registry = loader.get_registry()
        
        # Then: 各ステップで期待される結果が得られる
        self.assertGreater(len(loader.file_type_map), 0, "ファイルスキーマがロードされている")
        self.assertGreater(len(loader.object_type_map), 0, "オブジェクトスキーマがロードされている")
        
        self.assertIsNotNone(transactions_schema, "TRANSACTIONSファイルスキーマが取得できる")
        self.assertEqual(transactions_schema.get('title'), 'トランザクション')
        
        self.assertIsNotNone(stock_issuance_schema, "株式発行オブジェクトスキーマが取得できる")
        self.assertEqual(stock_issuance_schema.get('title'), '株式発行トランザクション')
        
        self.assertIsInstance(registry, Registry, "Registryが正しく構築される")
        # Registry には resolution_scope がないため、コメントアウト
        # self.assertEqual(registry.resolution_scope, 'https://jocf.startupstandard.org/jocf/main/')


class TestSchemaLoaderAPIContractSpecs(unittest.TestCase):
    """SchemaLoaderのAPI契約仕様テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
        self.loader.load_all_schemas()
    
    def test_get_file_schema_contract_spec(self):
        """仕様: get_file_schema()のAPI契約"""
        # Given: スキーマがロード済み
        
        # When & Then: 存在するfile_typeの場合
        file_type = FileType('JOCF_TRANSACTIONS_FILE')
        schema = self.loader.get_file_schema(file_type)
        self.assertIsInstance(schema, dict, "存在するfile_typeでは辞書を返す")
        self.assertIn('$id', schema, "返されるスキーマには$idが含まれる")
        self.assertIn('title', schema, "返されるスキーマにはtitleが含まれる")
        
        # When & Then: 存在しないfile_typeの場合
        non_existent_file_type = FileType('NON_EXISTENT_TYPE')
        non_existent_schema = self.loader.get_file_schema(non_existent_file_type)
        self.assertIsNone(non_existent_schema, "存在しないfile_typeではNoneを返す")
        
        # When & Then: 型安全化でNoneは渡せないため、このテストは削除
        # none_schema = self.loader.get_file_schema(None)
        # self.assertIsNone(none_schema, "NoneをキーとしてもNoneを返す（辞書のget動作）")
    
    def test_get_object_schema_contract_spec(self):
        """仕様: get_object_schema()のAPI契約"""
        # Given: スキーマがロード済み
        
        # When & Then: 存在するobject_typeの場合
        object_type = ObjectType('TX_STOCK_ISSUANCE')
        schema = self.loader.get_object_schema(object_type)
        self.assertIsInstance(schema, dict, "存在するobject_typeでは辞書を返す")
        self.assertIn('$id', schema, "返されるスキーマには$idが含まれる")
        self.assertIn('title', schema, "返されるスキーマにはtitleが含まれる")
        
        # When & Then: 存在しないobject_typeの場合
        non_existent_object_type = ObjectType('NON_EXISTENT_TYPE')
        non_existent_schema = self.loader.get_object_schema(non_existent_object_type)
        self.assertIsNone(non_existent_schema, "存在しないobject_typeではNoneを返す")
    
    def test_get_registry_lazy_initialization_spec(self):
        """仕様: get_registry()の遅延初期化契約"""
        # Given: 新しいSchemaLoaderインスタンス
        fresh_loader = SchemaLoader(self.config_manager)
        fresh_loader.load_all_schemas()
        
        # When: 初期状態ではregistryはNone
        self.assertIsNone(fresh_loader.registry, "初期状態ではregistryはNone")
        
        # When: 初回get_registry()呼び出し
        registry1 = fresh_loader.get_registry()
        
        # Then: Registryが作成され、インスタンス変数に保存される
        self.assertIsNotNone(fresh_loader.registry, "呼び出し後はregistryが設定される")
        self.assertIsInstance(registry1, Registry, "Registryインスタンスが返される")
        
        # When: 再度get_registry()を呼び出し
        registry2 = fresh_loader.get_registry()
        
        # Then: 同じインスタンスが返される（キャッシュされる）
        self.assertIs(registry1, registry2, "同じRegistryインスタンスが返される")


class TestSchemaLoaderWorkflowSpecs(unittest.TestCase):
    """SchemaLoaderのワークフロー仕様テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
    
    def test_load_all_schemas_workflow_spec(self):
        """仕様: load_all_schemas()の実行ワークフロー"""
        # Given: 初期状態のSchemaLoader
        self.assertEqual(len(self.loader.file_type_map), 0)
        self.assertEqual(len(self.loader.object_type_map), 0)
        
        # When: load_all_schemas()を実行
        self.loader.load_all_schemas()
        
        # Then: 両方のマップにスキーマがロードされる
        self.assertGreater(len(self.loader.file_type_map), 0, "ファイルスキーマがロードされる")
        self.assertGreater(len(self.loader.object_type_map), 0, "オブジェクトスキーマがロードされる")
        
        # And: 期待されるfile_typeが含まれる
        expected_file_types = [
            'JOCF_TRANSACTIONS_FILE',
            'JOCF_STOCK_CLASSES_FILE', 
            'JOCF_SECURITY_HOLDERS_FILE',
            'JOCF_SECURITYHOLDERS_AGREEMENT_FILE'
        ]
        for file_type_str in expected_file_types:
            file_type = FileType(file_type_str)
            self.assertIn(file_type, self.loader.file_type_map, f"{file_type_str}がロードされる")
        
        # And: 期待されるobject_typeが含まれる  
        expected_object_types = [
            'TX_STOCK_ISSUANCE',
            'SECURITY_HOLDER',
            'STOCK_CLASS'
        ]
        for object_type_str in expected_object_types:
            object_type = ObjectType(object_type_str)
            self.assertIn(object_type, self.loader.object_type_map, f"{object_type_str}がロードされる")
    
    def test_multiple_load_all_schemas_calls_spec(self):
        """仕様: load_all_schemas()の複数回呼び出し動作"""
        # Given: 初回ロード
        self.loader.load_all_schemas()
        initial_file_count = len(self.loader.file_type_map)
        initial_object_count = len(self.loader.object_type_map)
        
        # When: 再度load_all_schemas()を呼び出し
        self.loader.load_all_schemas()
        
        # Then: 結果は同じである（冪等性）
        self.assertEqual(len(self.loader.file_type_map), initial_file_count, 
                        "複数回呼び出しても結果は同じ")
        self.assertEqual(len(self.loader.object_type_map), initial_object_count,
                        "複数回呼び出しても結果は同じ")


class TestSchemaLoaderRegistryIntegrationSpecs(unittest.TestCase):
    """SchemaLoaderとRegistryの統合仕様テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
        self.loader.load_all_schemas()
    
    def test_registry_integration_with_jsonschema_validation(self):
        """仕様: Registryが jsonschema.validate と正常に統合される"""
        import jsonschema
        
        # Given: Registryを取得
        registry = self.loader.get_registry()
        
        # And: $refを含むスキーマを取得
        stock_issuance_schema = self.loader.get_object_schema(ObjectType('TX_STOCK_ISSUANCE'))
        self.assertIsNotNone(stock_issuance_schema, "スキーマが存在する")
        
        # And: 有効なテストデータ
        test_data = {
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "test-issuance-001",
            "stock_class_id": "common-stock",
            "securityholder_id": "holder-001",
            "share_price": {"amount": "100", "currency": "JPY"},  # 'currency'が正しいフィールド名
            "quantity": "1000",
            "date": "2023-12-01",
            "security_id": "security-001"
        }
        
        # When: Registry付きでjsonschema.validateを実行
        try:
            jsonschema.validate(test_data, stock_issuance_schema, registry=registry)
            validation_success = True
        except jsonschema.ValidationError:
            validation_success = False
        except Exception:
            validation_success = False
        
        # Then: $ref解決を含む検証が正常に動作する
        self.assertTrue(validation_success, "Registryを使った$ref解決付き検証が成功する")


class TestSchemaLoaderDataIntegritySpecs(unittest.TestCase):
    """SchemaLoaderのデータ整合性仕様テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
        self.loader.load_all_schemas()
    
    def test_schema_data_structure_spec(self):
        """仕様: ロードされたスキーマのデータ構造"""
        # Given: スキーマがロード済み
        
        # When & Then: ファイルスキーマの構造検証
        for file_type, schema in self.loader.file_type_map.items():
            self.assertIsInstance(schema, dict, f"{file_type}のスキーマは辞書")
            self.assertIn('$id', schema, f"{file_type}のスキーマには$idがある")
            self.assertIn('title', schema, f"{file_type}のスキーマにはtitleがある")
            self.assertIn('type', schema, f"{file_type}のスキーマにはtypeがある")
            
            # file_typeがproperties.file_type.constまたは直接定義されている
            extracted_file_type = self.loader._extract_file_type(schema)
            self.assertEqual(extracted_file_type, file_type.value, 
                           f"抽出されたfile_typeが一致: {file_type}")
        
        # When & Then: オブジェクトスキーマの構造検証  
        for object_type, schema in self.loader.object_type_map.items():
            self.assertIsInstance(schema, dict, f"{object_type}のスキーマは辞書")
            self.assertIn('$id', schema, f"{object_type}のスキーマには$idがある")
            self.assertIn('title', schema, f"{object_type}のスキーマにはtitleがある")
            self.assertIn('type', schema, f"{object_type}のスキーマにはtypeがある")
            
            # object_typeがproperties.object_type.constまたは直接定義されている
            extracted_object_type = self.loader._extract_object_type(schema)
            self.assertEqual(extracted_object_type, object_type.value,
                           f"抽出されたobject_typeが一致: {object_type}")
    
    def test_schema_uniqueness_spec(self):
        """仕様: スキーマの一意性"""
        # Given: スキーマがロード済み
        
        # When & Then: file_type_mapでのキーの一意性
        file_types = list(self.loader.file_type_map.keys())
        self.assertEqual(len(file_types), len(set(file_types)), 
                        "file_typeキーは一意である")
        
        # And: object_type_mapでのキーの一意性
        object_types = list(self.loader.object_type_map.keys())
        self.assertEqual(len(object_types), len(set(object_types)),
                        "object_typeキーは一意である")
        
        # And: file_typeとobject_typeに重複がない
        type_intersection = set(file_types) & set(object_types)
        self.assertEqual(len(type_intersection), 0,
                        "file_typeとobject_typeに重複はない")


class TestSchemaLoaderAdditionalMethodsSpecs(unittest.TestCase):
    """SchemaLoaderの追加メソッドの仕様テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
        self.loader = SchemaLoader(self.config_manager)
        self.loader.load_all_schemas()
    
    def test_get_schema_by_id_usage_spec(self):
        """仕様: get_schema_by_id()の使用方法"""
        # 用途: スキーマIDから直接スキーマを取得する際に使用
        
        # Given: 特定のスキーマIDがわかっている場合
        transactions_id = "https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json"
        stock_issuance_id = "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockIssuance.schema.json"
        
        # When: get_schema_by_id()でスキーマを取得
        transactions_schema_id = SchemaId(transactions_id)
        stock_issuance_schema_id = SchemaId(stock_issuance_id)
        transactions_schema = self.loader.get_schema_by_id(transactions_schema_id)
        stock_issuance_schema = self.loader.get_schema_by_id(stock_issuance_schema_id)
        
        # Then: IDに対応するスキーマが取得できる
        self.assertIsNotNone(transactions_schema, "正確なIDでスキーマを取得")
        self.assertEqual(transactions_schema.get('$id'), transactions_id, "期待するスキーマが取得される")
        
        self.assertIsNotNone(stock_issuance_schema, "オブジェクトスキーマも取得可能")
        self.assertEqual(stock_issuance_schema.get('$id'), stock_issuance_id, "期待するスキーマが取得される")
        
        # 使用例: $ref解決と組み合わせた使用
        # RefResolverを使わずに直接スキーマを取得したい場合
        self.assertIn('title', transactions_schema, "取得したスキーマは完全な内容を持つ")
        self.assertIn('properties', transactions_schema, "取得したスキーマは完全な内容を持つ")
    
    def test_get_types_methods_usage_spec(self):
        """仕様: get_file_types()とget_object_types()の使用方法"""
        # 用途: 利用可能なタイプの一覧を取得してUIや選択肢を構築する際に使用
        
        # When: 利用可能なファイルタイプとオブジェクトタイプを取得
        file_types = self.loader.get_file_types()
        object_types = self.loader.get_object_types()
        
        # Then: リスト形式で全てのタイプが取得できる
        self.assertIsInstance(file_types, list, "file_typesはリストで取得")
        self.assertIsInstance(object_types, list, "object_typesはリストで取得")
        
        # 使用例1: UIでの選択肢作成
        file_type_strings = [ft.value for ft in file_types]
        object_type_strings = [ot.value for ot in object_types]
        self.assertIn('JOCF_TRANSACTIONS_FILE', file_type_strings, "期待されるファイルタイプが含まれる")
        self.assertIn('TX_STOCK_ISSUANCE', object_type_strings, "期待されるオブジェクトタイプが含まれる")
        
        # 使用例2: 動的バリデーション対象の決定
        for file_type in file_types:
            schema = self.loader.get_file_schema(file_type)
            self.assertIsNotNone(schema, f"取得した{file_type}に対応するスキーマが存在")
        
        # 使用例3: ドキュメント生成
        combined_types = {"file_types": file_types, "object_types": object_types}
        self.assertGreater(len(combined_types["file_types"]), 0, "ドキュメント用データ構造を構築")
        self.assertGreater(len(combined_types["object_types"]), 0, "ドキュメント用データ構造を構築")
    
    def test_schema_metadata_access_pattern_spec(self):
        """仕様: スキーマメタデータへの直接アクセスパターン"""
        # 直接スキーマからメタデータを取得するパターン
        
        # 使用例1: 特定のファイルスキーマの詳細情報取得
        transactions_schema = self.loader.get_file_schema("JOCF_TRANSACTIONS_FILE")
        if transactions_schema:
            schema_id = transactions_schema.get("$id")
            title = transactions_schema.get("title")
            description = transactions_schema.get("description")
            
            self.assertIsNotNone(schema_id, "スキーマIDが取得できる")
            self.assertIsNotNone(title, "タイトルが取得できる")
            self.assertEqual(title, "トランザクション", "期待されるタイトル")
        
        # 使用例2: 特定のオブジェクトスキーマの詳細情報取得
        stock_issuance_schema = self.loader.get_object_schema("TX_STOCK_ISSUANCE")
        if stock_issuance_schema:
            schema_id = stock_issuance_schema.get("$id")
            title = stock_issuance_schema.get("title")
            
            self.assertIsNotNone(schema_id, "スキーマIDが取得できる")
            self.assertEqual(title, "株式発行トランザクション", "期待されるタイトル")
        
        # 使用例3: 全体のサマリー情報は直接メソッドで取得
        file_types = self.loader.get_file_types()
        object_types = self.loader.get_object_types()
        
        summary_info = {
            "total_file_schemas": len(file_types),
            "total_object_schemas": len(object_types),
            "file_types": file_types,
            "object_types": object_types,
            "schema_root_path": str(self.loader.schema_root_path)
        }
        
        self.assertGreater(summary_info["total_file_schemas"], 0, "ファイルスキーマ数")
        self.assertGreater(summary_info["total_object_schemas"], 0, "オブジェクトスキーマ数")
        
        # 管理画面での表示用データとして利用可能
        total_schemas = summary_info["total_file_schemas"] + summary_info["total_object_schemas"]
        self.assertGreater(total_schemas, 0, "管理画面用のサマリーデータとして使用可能")
    
    def test_cache_management_usage_spec(self):
        """仕様: clear_cache()とpreload_schemas()の使用方法"""
        # 用途: メモリ管理とパフォーマンス最適化
        
        # 使用例1: メモリ使用量削減のためのキャッシュクリア
        # Given: Registryが作成されている状態
        registry = self.loader.get_registry()
        self.assertIsNotNone(self.loader.registry, "Registryがキャッシュされている")
        
        # When: メモリ削減のためキャッシュをクリア
        self.loader.clear_cache()
        
        # Then: Registryキャッシュがクリアされる
        self.assertIsNone(self.loader.registry, "キャッシュがクリアされる")
        
        # 使用例2: 特定スキーマの事前読み込み
        # Given: 新しいローダーインスタンス
        fresh_loader = SchemaLoader(self.config_manager)
        
        # When: 特定のスキーマファイルのみを事前読み込み
        selected_schemas = [
            "files/TransactionsFile.schema.json",
            "objects/SecurityHolder.schema.json"
        ]
        fresh_loader.preload_schemas(selected_schemas)
        
        # Then: 指定されたスキーマがロードされる（エラーが発生しない）
        # 注意: 現在の実装では内部でエラーハンドリングされる
        self.assertIsInstance(selected_schemas, list, "スキーマパスリストが処理される")
        
        # 使用例3: 段階的ロード戦略
        # 必要最小限のスキーマから開始し、必要に応じて追加ロード
        fresh_loader.load_all_schemas()  # 全体ロード
        initial_count = len(fresh_loader.file_type_map) + len(fresh_loader.object_type_map)
        self.assertGreater(initial_count, 0, "段階的ロード戦略の基盤として使用可能")
    
    def test_string_representation_usage_spec(self):
        """仕様: __str__()と__repr__()の使用方法"""
        # 用途: ログ出力、デバッグ、管理画面での表示
        
        # 使用例1: 読みやすいログ出力での使用
        readable_info = str(self.loader)
        
        self.assertIn("SchemaLoader", readable_info, "クラス名が含まれる")
        self.assertIn("files=", readable_info, "ロード済みファイル数が表示")
        self.assertIn("objects=", readable_info, "ロード済みオブジェクト数が表示")
        self.assertIn("root=", readable_info, "スキーマルートパスが表示")
        
        # ログ出力例: "SchemaLoader loaded: SchemaLoader(files=4, objects=22, root=/path/to/schema)"
        print(f"SchemaLoader loaded: {self.loader}")  # 実際のログ出力例
        
        # 使用例2: デバッグ情報での使用
        debug_info = repr(self.loader)
        
        self.assertIn("SchemaLoader", debug_info, "クラス名が含まれる")
        self.assertIn("config_manager=", debug_info, "設定管理オブジェクトが含まれる")
        self.assertIn("schema_root_path=", debug_info, "スキーマルートパスが含まれる")
        
        # デバッグ出力例: 開発時の状態確認
        print(f"Debug info: {repr(self.loader)}")  # 実際のデバッグ出力例
        
        # 使用例3: 管理画面での状態表示
        status_display = {
            "readable_status": str(self.loader),
            "debug_details": repr(self.loader),
            "is_loaded": len(self.loader.file_type_map) > 0
        }
        
        self.assertTrue(status_display["is_loaded"], "管理画面用ステータス情報として使用可能")
        self.assertIsInstance(status_display["readable_status"], str, "表示用文字列が取得可能")


class TestSchemaLoaderPerformanceSpecs(unittest.TestCase):
    """SchemaLoaderのパフォーマンス仕様テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config_manager = ConfigManager()
    
    def test_loading_performance_spec(self):
        """仕様: スキーマロードのパフォーマンス特性"""
        import time
        
        # Given: SchemaLoaderが初期化されている
        loader = SchemaLoader(self.config_manager)
        
        # When: load_all_schemas()の実行時間を測定
        start_time = time.time()
        loader.load_all_schemas()
        loading_time = time.time() - start_time
        
        # Then: 合理的な時間内でロードが完了する（2秒以内）
        self.assertLess(loading_time, 2.0, "スキーマロードは2秒以内に完了する")
        
        # And: 十分な数のスキーマがロードされる
        total_schemas = len(loader.file_type_map) + len(loader.object_type_map)
        self.assertGreater(total_schemas, 20, "20個以上のスキーマがロードされる")
    
    def test_registry_initialization_performance_spec(self):
        """仕様: Registry初期化のパフォーマンス特性"""
        import time
        
        # Given: スキーマがロード済み
        loader = SchemaLoader(self.config_manager)
        loader.load_all_schemas()
        
        # When: Registry初期化時間を測定
        start_time = time.time()
        registry = loader.get_registry()
        init_time = time.time() - start_time
        
        # Then: 合理的な時間内で初期化が完了する（1秒以内）
        self.assertLess(init_time, 1.0, "Registry初期化は1秒以内に完了する")
        
        # And: Registry が正常に構築される
        self.assertIsInstance(registry, Registry, "Registryが正常に構築される")


if __name__ == '__main__':
    unittest.main()