#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ObjectValidator使用方法説明テスト

ObjectValidatorクラスの使い方を実際のコード例で説明するテストファイルです。
このテストは仕様書としても機能し、開発者がObjectValidatorを理解するのに役立ちます。

注意: このテストは教育・説明目的であり、実際のSchemaLoaderクラスを使用しますが、
      テスト用のサンプルスキーマを手動で設定して動作を説明します。
"""

import unittest
from unittest.mock import Mock, patch
from jsonschema import ValidationError, RefResolver

# テスト対象のクラス
from validator.object_validator import ObjectValidator
from validator.schema_loader import SchemaLoader
from validator.config_manager import ConfigManager
from validator.validation_result import ValidationResult


class TestObjectValidatorSpecs(unittest.TestCase):
    """ObjectValidatorの使用方法説明テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # ConfigManagerのモックを作成（ファイルシステムに依存しないため）
        self.mock_config = Mock(spec=ConfigManager)
        
        # 実際のSchemaLoaderを作成し、初期化をスキップ
        self.schema_loader = SchemaLoader.__new__(SchemaLoader)
        self.schema_loader.logger = Mock()
        self.schema_loader.config_manager = self.mock_config
        self.schema_loader.schema_root_path = Mock()
        self.schema_loader.file_type_map = {}
        self.schema_loader.object_type_map = {}
        self.schema_loader.ref_resolver = None
        
        # テスト用スキーマを手動で設定（実際のファイル読み込みの代わり）
        self.setup_test_schemas()
        
        # RefResolverのモックを設定（Path操作を回避）
        mock_resolver = Mock(spec=RefResolver)
        mock_resolver.store = {}
        self.schema_loader.get_ref_resolver = Mock(return_value=mock_resolver)
        
        # ObjectValidatorのインスタンスを作成
        self.validator = ObjectValidator(self.schema_loader)
    
    def setup_test_schemas(self):
        """テスト用のスキーマを手動で設定"""
        # 株式発行スキーマ
        stock_issuance_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockIssuance.schema.json",
            "title": "株式発行トランザクション",
            "type": "object",
            "properties": {
                "object_type": {"const": "TX_STOCK_ISSUANCE"},
                "id": {"type": "string"},
                "stock_class_id": {"type": "string"},
                "quantity": {"type": "string"},
                "date": {"type": "string", "format": "date"}
            },
            "required": ["object_type", "id", "stock_class_id", "quantity", "date"],
            "additionalProperties": False
        }
        
        # 証券保有者スキーマ
        security_holder_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/SecurityHolder.schema.json",
            "title": "証券保有者",
            "type": "object", 
            "properties": {
                "object_type": {"const": "SECURITY_HOLDER"},
                "id": {"type": "string"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["object_type", "id", "name"],
            "additionalProperties": False
        }
        
        # スキーマを手動で登録
        self.schema_loader.object_type_map = {
            "TX_STOCK_ISSUANCE": stock_issuance_schema,
            "SECURITY_HOLDER": security_holder_schema
        }

    def test_basic_usage_single_object_validation(self):
        """
        基本的な使い方: 単一オブジェクトの検証
        
        ObjectValidatorの最も基本的な使用方法を示します。
        1. SchemaLoaderとConfigManagerを準備
        2. ObjectValidatorインスタンスを作成
        3. validate_object()メソッドで検証実行
        4. ValidationResultから結果を取得
        """
        # === 準備: 有効なJOCFオブジェクト ===
        valid_stock_issuance = {
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "stock-issuance-001",
            "stock_class_id": "common-stock",
            "quantity": "1000",
            "date": "2023-12-01"
        }
        
        # === 実行: オブジェクトの検証 ===
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None  # 検証成功
            
            result = self.validator.validate_object(valid_stock_issuance)
        
        # === 結果確認: 検証が成功することを確認 ===
        self.assertTrue(result.is_valid, "有効なオブジェクトは検証に成功する")
        self.assertEqual(len(result.errors), 0, "成功時はエラーがない")
        
        # === 使用方法の説明 ===
        print(f"""
        ✅ 基本的な使い方:
        
        # 1. 設定とスキーマローダーを初期化
        config_manager = ConfigManager("path/to/config.json")
        schema_loader = SchemaLoader(config_manager)
        schema_loader.load_all_schemas()  # スキーマファイルを読み込み
        
        # 2. ObjectValidatorを初期化
        validator = ObjectValidator(schema_loader)
        
        # 3. オブジェクトを検証
        jocf_object = {{
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "stock-issuance-001",
            "stock_class_id": "common-stock",
            "quantity": "1000",
            "date": "2023-12-01"
        }}
        result = validator.validate_object(jocf_object)
        
        # 4. 結果を確認
        if result.is_valid:
            print("検証成功!")
        else:
            print(f"検証失敗: {{result.errors}}")
        """)

    def test_error_handling_missing_object_type(self):
        """
        エラーハンドリング: object_type属性が存在しない場合
        
        JOCFオブジェクトには必須のobject_type属性が必要です。
        この属性がない場合のエラーハンドリングを示します。
        """
        # === 準備: object_typeが存在しないオブジェクト ===
        invalid_object = {
            "id": "missing-object-type",
            "name": "テストオブジェクト"
        }
        
        # === 実行: 検証実行 ===
        result = self.validator.validate_object(invalid_object)
        
        # === 結果確認: 適切なエラーメッセージが返される ===
        self.assertFalse(result.is_valid, "object_typeが存在しない場合は検証失敗")
        self.assertIn("object_type属性が存在しません", result.errors[0])
        
        print(f"""
        ❌ エラーケース1 - object_type属性なし:
        
        invalid_object = {{"id": "test", "name": "名前"}}  # object_typeなし
        result = validator.validate_object(invalid_object)
        
        # result.is_valid == False
        # result.errors == ["{result.errors[0]}"]
        
        対処法: すべてのJOCFオブジェクトには"object_type"属性が必要です
        """)

    def test_error_handling_invalid_object_type(self):
        """
        エラーハンドリング: 無効なobject_type
        
        object_typeは文字列である必要があり、サポートされている値でなければなりません。
        """
        # === ケース1: object_typeが文字列でない ===
        invalid_object_non_string = {
            "object_type": 123,  # 数値
            "id": "test"
        }
        
        result = self.validator.validate_object(invalid_object_non_string)
        self.assertFalse(result.is_valid)
        self.assertIn("object_type属性は文字列である必要があります", result.errors[0])
        
        # === ケース2: サポートされていないobject_type ===
        invalid_object_unknown_type = {
            "object_type": "UNKNOWN_OBJECT_TYPE",
            "id": "test"
        }
        
        result = self.validator.validate_object(invalid_object_unknown_type)
        self.assertFalse(result.is_valid)
        self.assertIn("に対応するスキーマが見つかりません", result.errors[0])
        
        print(f"""
        ❌ エラーケース2 - 無効なobject_type:
        
        # 文字列でない場合
        invalid1 = {{"object_type": 123}}
        
        # サポートされていない値の場合  
        invalid2 = {{"object_type": "UNKNOWN_TYPE"}}
        
        どちらも検証に失敗し、適切なエラーメッセージが返されます。
        
        対処法: 
        - object_typeは文字列で指定
        - サポートされているobject_typeのリストは get_supported_object_types() で確認可能
        """)

    def test_schema_validation_errors(self):
        """
        スキーマ検証エラー: JSONSchemaの検証に失敗した場合
        
        object_typeは有効だが、オブジェクトの内容がスキーマに適合しない場合。
        """
        # === 準備: 必須フィールドが不足したオブジェクト ===
        incomplete_object = {
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "incomplete-001"
            # "stock_class_id", "quantity", "date" が不足
        }
        
        # === 実行: JSONSchemaの検証で失敗させる ===
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = ValidationError("'stock_class_id' is a required property")
            
            result = self.validator.validate_object(incomplete_object)
        
        # === 結果確認 ===
        self.assertFalse(result.is_valid)
        self.assertTrue(any("JSONスキーマ検証エラー" in error for error in result.errors))
        
        print(f"""
        ❌ エラーケース3 - スキーマ検証失敗:
        
        incomplete_object = {{
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "test"
            # 必須フィールドが不足
        }}
        
        # JSONSchemaによる詳細な検証でエラーが検出される
        # result.errors に具体的なエラー内容が含まれる
        
        対処法:
        - スキーマの"required"配列に指定されたフィールドをすべて含める
        - 各フィールドの型や制約（format、pattern等）を確認
        """)

    def test_multiple_objects_validation(self):
        """
        複数オブジェクトの一括検証
        
        validate_objects()メソッドを使用して複数のオブジェクトを一度に検証。
        """
        # === 準備: 複数のオブジェクト（一部有効、一部無効）===
        objects = [
            {
                "object_type": "TX_STOCK_ISSUANCE",
                "id": "valid-001",
                "stock_class_id": "common",
                "quantity": "100",
                "date": "2023-12-01"
            },
            {
                "object_type": "SECURITY_HOLDER", 
                "id": "valid-002",
                "name": "山田太郎",
                "email": "yamada@example.com"
            },
            {
                "object_type": "INVALID_TYPE",  # 無効なobject_type
                "id": "invalid-001"
            }
        ]
        
        # === 実行: 一括検証 ===
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None  # 有効なオブジェクトは成功
            
            result = self.validator.validate_objects(objects)
        
        # === 結果確認 ===
        self.assertFalse(result.is_valid, "一部無効なオブジェクトがあるため全体として失敗")
        self.assertTrue(any("Object 2:" in error for error in result.errors), "3番目のオブジェクトでエラー")
        
        print(f"""
        📋 複数オブジェクトの一括検証:
        
        objects = [valid_obj1, valid_obj2, invalid_obj3]
        result = validator.validate_objects(objects)
        
        # 一つでも無効なオブジェクトがあれば全体として失敗
        # エラーメッセージにはどのオブジェクト（インデックス）でエラーが発生したかが含まれる
        # 例: "Object 2: object_type 'INVALID_TYPE' に対応するスキーマが見つかりません"
        
        実用的な使い方:
        - 大量のJOCFオブジェクトのバッチ検証に便利
        - エラーのあるオブジェクトを特定して修正可能
        """)

    def test_utility_methods(self):
        """
        ユーティリティメソッドの使用方法
        
        ObjectValidatorが提供する便利なメソッドの使い方を示します。
        """
        # === object_typeの取得 ===
        test_object = {"object_type": "TX_STOCK_ISSUANCE", "id": "test"}
        object_type = self.validator.get_object_type(test_object)
        self.assertEqual(object_type, "TX_STOCK_ISSUANCE")
        
        # === object_typeの有効性確認 ===
        is_valid = self.validator.is_valid_object_type("TX_STOCK_ISSUANCE")
        self.assertTrue(is_valid)
        
        is_invalid = self.validator.is_valid_object_type("UNKNOWN_TYPE")
        self.assertFalse(is_invalid)
        
        # === サポートされているobject_typeの一覧取得 ===
        supported_types = self.validator.get_supported_object_types()
        self.assertIsInstance(supported_types, list)
        self.assertIn("TX_STOCK_ISSUANCE", supported_types)
        
        # === オブジェクト構造の基本チェック ===
        structure_result = self.validator.validate_object_structure(test_object)
        self.assertTrue(structure_result.is_valid)
        
        # === 空オブジェクトの構造チェック ===
        empty_structure_result = self.validator.validate_object_structure({})
        self.assertFalse(empty_structure_result.is_valid)
        
        print(f"""
        🔧 ユーティリティメソッドの活用:
        
        # 1. object_typeの取得
        obj_type = validator.get_object_type(obj)  # => "TX_STOCK_ISSUANCE"
        
        # 2. object_typeの有効性確認
        is_valid = validator.is_valid_object_type("TX_STOCK_ISSUANCE")  # => True
        is_invalid = validator.is_valid_object_type("UNKNOWN_TYPE")     # => False
        
        # 3. サポートされているタイプ一覧
        types = validator.get_supported_object_types()  
        # => ["TX_STOCK_ISSUANCE", "SECURITY_HOLDER", ...]
        
        # 4. 基本構造チェック（辞書型か、空でないかなど）
        structure_result = validator.validate_object_structure(obj)
        
        実用的な活用例:
        - データ処理前の事前チェック
        - エラー原因の段階的な特定
        - 対応可能なobject_typeの確認
        """)

    def test_schema_operations(self):
        """
        スキーマ操作
        
        オブジェクトに対応するスキーマの取得と検証方法を示します。
        """
        test_object = {
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "test-001"
        }
        
        # === オブジェクトに対応するスキーマの取得 ===
        schema = self.validator.get_schema_for_object(test_object)
        self.assertIsNotNone(schema)
        self.assertEqual(schema["title"], "株式発行トランザクション")
        
        # === 指定スキーマでの検証 ===
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            result = self.validator.validate_object_with_schema(test_object, schema)
            self.assertTrue(result.is_valid)
        
        # === $ref解決を含む検証 ===
        ref_result = self.validator.validate_with_ref_resolution(test_object, schema)
        self.assertIsInstance(ref_result, ValidationResult)
        
        print(f"""
        📄 スキーマ操作:
        
        # 1. オブジェクトに対応するスキーマを自動取得
        schema = validator.get_schema_for_object(obj)
        # => {{"title": "株式発行トランザクション", "type": "object", ...}}
        
        # 2. 指定したスキーマで直接検証
        result = validator.validate_object_with_schema(obj, custom_schema)
        
        # 3. $ref解決を含む検証（複雑なスキーマ参照に対応）
        result = validator.validate_with_ref_resolution(obj, schema_with_refs)
        
        実用的な活用例:
        - カスタムスキーマでの検証
        - スキーマの詳細情報取得
        - 複雑な$ref構造のデバッグ
        """)

    def test_complete_workflow_example(self):
        """
        完全なワークフロー例
        
        ObjectValidatorを使った実際のプロジェクトでの典型的な使用方法を示します。
        """
        print("""
        🚀 実際のプロジェクトでの完全なワークフロー例:
        
        # === 1. 初期化とセットアップ ===
        from validator.config_manager import ConfigManager
        from validator.schema_loader import SchemaLoader
        from validator.object_validator import ObjectValidator
        
        # 設定ファイルからConfigManagerを作成
        config = ConfigManager("/path/to/validator_config.json")
        
        # SchemaLoaderでスキーマを読み込み
        schema_loader = SchemaLoader(config)
        schema_loader.load_all_schemas()  # schema/配下のファイルを自動読み込み
        
        # ObjectValidatorを初期化
        validator = ObjectValidator(schema_loader)
        validator.set_strict_mode(True)  # 厳密モードで検証
        
        # === 2. 単一オブジェクトの検証 ===
        jocf_object = {{
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "issuance-2023-001",
            "stock_class_id": "common-stock-class-1",
            "securityholder_id": "holder-founder-001",
            "share_price": {{"amount": "100", "currency_code": "JPY"}},
            "quantity": "1000",
            "date": "2023-12-01",
            "security_id": "security-001"
        }}
        
        result = validator.validate_object(jocf_object)
        
        if result.is_valid:
            print("✅ オブジェクトは有効なJOCFフォーマットです")
            # データベースに保存、API応答、ファイル出力など
        else:
            print("❌ 検証エラー:")
            for i, error in enumerate(result.errors, 1):
                print(f"  {{i}}. {{error}}")
            # エラーログ記録、ユーザーへの通知など
        
        # === 3. ファイル全体の検証（複数オブジェクト）===
        import json
        
        with open("/path/to/jocf_file.json", "r") as f:
            jocf_data = json.load(f)
        
        # ファイル内のオブジェクト配列を検証
        if "objects" in jocf_data:
            batch_result = validator.validate_objects(jocf_data["objects"])
            
            if batch_result.is_valid:
                print(f"✅ {{len(jocf_data['objects'])}}個のオブジェクトすべてが有効")
            else:
                print(f"❌ {{len(batch_result.errors)}}個のエラーが検出されました")
                for error in batch_result.errors:
                    print(f"  - {{error}}")
        
        # === 4. 統計情報とパフォーマンス監視 ===
        stats = validator.get_validation_stats()
        print(f"検証統計:")
        print(f"  - 総検証回数: {{stats['total_validations']}}")
        print(f"  - 成功率: {{stats['successful_validations']/stats['total_validations']*100:.1f}}%")
        print(f"  - 平均検証時間: {{sum(stats['validation_times'])/len(stats['validation_times']):.3f}}秒")
        
        # === 5. エラーハンドリングとロギング ===
        import logging
        
        logger = logging.getLogger('jocf_validator')
        
        def validate_and_log(obj, obj_id=None):
            try:
                result = validator.validate_object(obj)
                if result.is_valid:
                    logger.info(f"Validation success: {{obj_id or obj.get('id', 'unknown')}}")
                    return True
                else:
                    logger.warning(f"Validation failed for {{obj_id}}: {{result.errors}}")
                    return False
            except Exception as e:
                logger.error(f"Validation error for {{obj_id}}: {{e}}")
                return False
        
        # === 6. カスタムバリデーターの追加（オプション）===
        def business_rule_validator(data):
            # 独自のビジネスルール検証
            if data.get("object_type") == "TX_STOCK_ISSUANCE":
                quantity = int(data.get("quantity", 0))
                if quantity > 1000000:  # 100万株を超える発行は要確認
                    return False
            return True
            
        validator.add_custom_validator("business_rules", business_rule_validator)
        
        このワークフローは、JOCFファイルの検証、データ処理、
        エラーハンドリングを含む実用的な例を示しています。
        """)


if __name__ == '__main__':
    # テスト実行時に詳細な使用方法説明を表示
    unittest.main(verbosity=2)