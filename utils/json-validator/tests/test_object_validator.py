#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ObjectValidatorクラスの単体テスト

テスト対象：
- object_type属性による適切なスキーマ特定
- jsonschema.validateを使った完全検証
- $ref解決を含むスキーマ検証
- object_type不正・未定義時のエラーハンドリング
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import jsonschema
from jsonschema import ValidationError, RefResolver

# テスト対象のクラス（実装予定）
from validator.object_validator import ObjectValidator
from validator.schema_loader import SchemaLoader
from validator.exceptions import ObjectValidationError
from validator.types import ObjectType




class TestObjectValidator(unittest.TestCase):
    """ObjectValidatorクラスのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        self.mock_schema_loader = Mock()
        self.object_validator = ObjectValidator(self.mock_schema_loader)
        
        # テスト用のスキーマデータ
        self.stock_issuance_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockIssuance.schema.json",
            "title": "株式発行トランザクション",
            "type": "object",
            "allOf": [
                {"$ref": "https://jocf.startupstandard.org/jocf/main/schema/primitives/objects/Object.schema.json"},
                {"$ref": "https://jocf.startupstandard.org/jocf/main/schema/primitives/objects/transactions/Transaction.schema.json"}
            ],
            "properties": {
                "object_type": {
                    "const": "TX_STOCK_ISSUANCE"
                },
                "id": {
                    "type": "string"
                },
                "stock_class_id": {
                    "type": "string"
                },
                "securityholder_id": {
                    "type": "string"
                },
                "share_price": {
                    "$ref": "https://jocf.startupstandard.org/jocf/main/schema/types/Monetary.schema.json"
                },
                "quantity": {
                    "type": "string"
                },
                "date": {
                    "type": "string",
                    "format": "date"
                },
                "security_id": {
                    "type": "string"
                }
            },
            "required": [
                "object_type", "id", "securityholder_id", "stock_class_id",
                "share_price", "quantity", "date", "security_id"
            ],
            "additionalProperties": False,
            "object_type": "TX_STOCK_ISSUANCE"
        }
        
        self.security_holder_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/SecurityHolder.schema.json",
            "title": "証券保有者",
            "type": "object",
            "properties": {
                "object_type": {
                    "const": "SECURITY_HOLDER"
                },
                "id": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "contact_info": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "format": "email"
                        },
                        "phone": {
                            "type": "string"
                        }
                    }
                }
            },
            "required": ["object_type", "id", "name"],
            "additionalProperties": False,
            "object_type": "SECURITY_HOLDER"
        }
        
        # テスト用の有効なオブジェクトデータ
        self.valid_stock_issuance = {
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
        }
        
        self.valid_security_holder = {
            "object_type": "SECURITY_HOLDER",
            "id": "test-securityholder-1",
            "name": "テスト投資家",
            "contact_info": {
                "email": "test@example.com",
                "phone": "090-1234-5678"
            }
        }
    
    def test_validate_object_success_stock_issuance(self):
        """正常系: 株式発行オブジェクトの検証成功"""
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        # jsonschema.validateが成功するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None  # 成功時はNoneを返す
            
            # テスト実行
            result = self.object_validator.validate_object(self.valid_stock_issuance)
            
            # 検証
            self.assertTrue(result.is_valid)
            self.assertEqual(len(result.errors), 0)
            # 型安全化でObjectType型で呼び出されることを確認
            expected_call = ObjectType("TX_STOCK_ISSUANCE")
            self.mock_schema_loader.get_object_schema.assert_called_once_with(expected_call)
            mock_validate.assert_called_once()
    
    def test_validate_object_success_security_holder(self):
        """正常系: 証券保有者オブジェクトの検証成功"""
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.security_holder_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        # jsonschema.validateが成功するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            # テスト実行
            result = self.object_validator.validate_object(self.valid_security_holder)
            
            # 検証
            self.assertTrue(result.is_valid)
            self.assertEqual(len(result.errors), 0)
            # 型安全化でObjectType型で呼び出されることを確認
            expected_call = ObjectType("SECURITY_HOLDER")
            self.mock_schema_loader.get_object_schema.assert_called_once_with(expected_call)
    
    def test_validate_object_missing_object_type(self):
        """異常系: object_type属性が存在しない"""
        # object_type属性を削除
        invalid_data = self.valid_stock_issuance.copy()
        del invalid_data["object_type"]
        
        # テスト実行
        result = self.object_validator.validate_object(invalid_data)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertIn("object_type属性が存在しません", result.errors)
    
    def test_validate_object_invalid_object_type_type(self):
        """異常系: object_type属性が文字列でない"""
        # object_type属性を数値に変更
        invalid_data = self.valid_stock_issuance.copy()
        invalid_data["object_type"] = 123
        
        # テスト実行
        result = self.object_validator.validate_object(invalid_data)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertIn("object_type属性は文字列である必要があります", result.errors)
    
    def test_validate_object_unknown_object_type(self):
        """異常系: 存在しないobject_type"""
        # 存在しないobject_typeを設定
        invalid_data = self.valid_stock_issuance.copy()
        invalid_data["object_type"] = "UNKNOWN_OBJECT_TYPE"
        
        # モックの設定（スキーマが見つからない）
        self.mock_schema_loader.get_object_schema.return_value = None
        
        # テスト実行
        result = self.object_validator.validate_object(invalid_data)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertIn("object_type 'UNKNOWN_OBJECT_TYPE' に対応するスキーマが見つかりません", result.errors)
    
    def test_validate_object_jsonschema_validation_error(self):
        """異常系: JSONスキーマ検証エラー"""
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        # jsonschema.validateが失敗するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = ValidationError("Required property 'id' is missing")
            
            # テスト実行
            result = self.object_validator.validate_object(self.valid_stock_issuance)
            
            # 検証
            self.assertFalse(result.is_valid)
            self.assertTrue(any("JSONスキーマ検証エラー" in error for error in result.errors))
    
    def test_validate_object_missing_required_fields(self):
        """異常系: 必須フィールドが不足"""
        # 必須フィールドを削除
        invalid_data = self.valid_stock_issuance.copy()
        del invalid_data["id"]
        
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        # jsonschema.validateが失敗するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = ValidationError("'id' is a required property")
            
            # テスト実行
            result = self.object_validator.validate_object(invalid_data)
            
            # 検証
            self.assertFalse(result.is_valid)
            self.assertTrue(any("JSONスキーマ検証エラー" in error for error in result.errors))
    
    def test_validate_object_invalid_field_type(self):
        """異常系: フィールドの型が不正"""
        # date フィールドを数値に変更
        invalid_data = self.valid_stock_issuance.copy()
        invalid_data["date"] = 20230101
        
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        # jsonschema.validateが失敗するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = ValidationError("20230101 is not of type 'string'")
            
            # テスト実行
            result = self.object_validator.validate_object(invalid_data)
            
            # 検証
            self.assertFalse(result.is_valid)
            self.assertTrue(any("JSONスキーマ検証エラー" in error for error in result.errors))
    
    def test_validate_object_additional_properties_not_allowed(self):
        """異常系: additionalProperties: false での追加プロパティ"""
        # 追加プロパティを含むデータ
        invalid_data = self.valid_stock_issuance.copy()
        invalid_data["extra_field"] = "not allowed"
        
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        # jsonschema.validateが失敗するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = ValidationError("Additional properties are not allowed ('extra_field' was unexpected)")
            
            # テスト実行
            result = self.object_validator.validate_object(invalid_data)
            
            # 検証
            self.assertFalse(result.is_valid)
            self.assertTrue(any("JSONスキーマ検証エラー" in error for error in result.errors))
    
    def test_validate_object_with_ref_resolution(self):
        """$ref解決を含むスキーマ検証"""
        # $refを含むスキーマ
        schema_with_ref = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/ComplexObject.schema.json",
            "title": "複雑なオブジェクト",
            "type": "object",
            "properties": {
                "object_type": {
                    "const": "COMPLEX_OBJECT"
                },
                "id": {
                    "type": "string"
                },
                "monetary_value": {
                    "$ref": "https://jocf.startupstandard.org/jocf/main/schema/types/Monetary.schema.json"
                }
            },
            "required": ["object_type", "id", "monetary_value"],
            "object_type": "COMPLEX_OBJECT"
        }
        
        # $refで参照されるスキーマ
        monetary_schema = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/types/Monetary.schema.json",
            "type": "object",
            "properties": {
                "amount": {"type": "string"},
                "currency_code": {"type": "string"}
            },
            "required": ["amount", "currency_code"]
        }
        
        # テストデータ
        test_data = {
            "object_type": "COMPLEX_OBJECT",
            "id": "test-complex-1",
            "monetary_value": {
                "amount": "1000",
                "currency_code": "JPY"
            }
        }
        
        # RefResolverの設定
        store = {
            "https://jocf.startupstandard.org/jocf/main/schema/types/Monetary.schema.json": monetary_schema
        }
        resolver = RefResolver(
            "https://jocf.startupstandard.org/jocf/main/",
            schema_with_ref,
            store=store
        )
        
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = schema_with_ref
        self.mock_schema_loader.get_ref_resolver.return_value = resolver
        
        # 実際のjsonschema.validateを使用してテスト
        with patch('jsonschema.validate', wraps=jsonschema.validate) as mock_validate:
            # テスト実行
            result = self.object_validator.validate_object(test_data)
            
            # 検証
            self.assertTrue(result.is_valid)
            self.assertEqual(len(result.errors), 0)
            mock_validate.assert_called_once_with(test_data, schema_with_ref, resolver=resolver)
    
    def test_validate_object_nested_ref_resolution_error(self):
        """異常系: ネストした$ref解決エラー"""
        # 解決できない$refを含むスキーマ
        schema_with_invalid_ref = {
            "$id": "https://jocf.startupstandard.org/jocf/main/schema/objects/InvalidRefObject.schema.json",
            "title": "無効な参照を持つオブジェクト",
            "type": "object",
            "properties": {
                "object_type": {
                    "const": "INVALID_REF_OBJECT"
                },
                "id": {
                    "type": "string"
                },
                "invalid_ref": {
                    "$ref": "https://jocf.startupstandard.org/jocf/main/schema/types/NonExistent.schema.json"
                }
            },
            "required": ["object_type", "id", "invalid_ref"],
            "object_type": "INVALID_REF_OBJECT"
        }
        
        test_data = {
            "object_type": "INVALID_REF_OBJECT",
            "id": "test-invalid-ref-1",
            "invalid_ref": {"some": "value"}
        }
        
        # 空のストアを持つRefResolver
        resolver = RefResolver(
            "https://jocf.startupstandard.org/jocf/main/",
            schema_with_invalid_ref,
            store={}
        )
        
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = schema_with_invalid_ref
        self.mock_schema_loader.get_ref_resolver.return_value = resolver
        
        # jsonschema.validateが$ref解決エラーで失敗するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = jsonschema.RefResolutionError("Unable to resolve reference")
            
            # テスト実行
            result = self.object_validator.validate_object(test_data)
            
            # 検証
            self.assertFalse(result.is_valid)
            self.assertTrue(any("JSONスキーマ検証エラー" in error for error in result.errors))
    
    def test_get_object_schema_method(self):
        """_get_object_schemaメソッドのテスト"""
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        
        # テスト実行
        object_type = ObjectType("TX_STOCK_ISSUANCE")
        schema = self.object_validator._get_object_schema(object_type)
        
        # 検証
        self.assertEqual(schema, self.stock_issuance_schema)
        # 型安全化でObjectType型で呼び出されることを確認
        expected_call = ObjectType("TX_STOCK_ISSUANCE")
        self.mock_schema_loader.get_object_schema.assert_called_once_with(expected_call)
    
    def test_validate_with_jsonschema_success(self):
        """_validate_with_jsonschemaメソッドの成功テスト"""
        # モックの設定
        resolver = Mock()
        self.mock_schema_loader.get_ref_resolver.return_value = resolver
        
        # jsonschema.validateが成功するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            # テスト実行
            result = self.object_validator._validate_with_jsonschema(
                self.valid_stock_issuance, self.stock_issuance_schema
            )
            
            # 検証
            self.assertTrue(result.is_valid)
            self.assertEqual(len(result.errors), 0)
            mock_validate.assert_called_once_with(
                self.valid_stock_issuance, self.stock_issuance_schema, resolver=resolver
            )
    
    def test_validate_with_jsonschema_failure(self):
        """_validate_with_jsonschemaメソッドの失敗テスト"""
        # モックの設定
        resolver = Mock()
        self.mock_schema_loader.get_ref_resolver.return_value = resolver
        
        # jsonschema.validateが失敗するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = ValidationError("Validation failed")
            
            # テスト実行
            result = self.object_validator._validate_with_jsonschema(
                self.valid_stock_issuance, self.stock_issuance_schema
            )
            
            # 検証
            self.assertFalse(result.is_valid)
            self.assertGreater(len(result.errors), 0)
            self.assertIn("JSONスキーマ検証エラー", result.errors[0])
    
    def test_validate_various_object_types(self):
        """様々なobject_typeのオブジェクト検証"""
        object_types_and_schemas = [
            ("TX_STOCK_ISSUANCE", self.stock_issuance_schema),
            ("SECURITY_HOLDER", self.security_holder_schema),
            ("TX_STOCK_TRANSFER", {
                "object_type": "TX_STOCK_TRANSFER",
                "properties": {
                    "object_type": {"const": "TX_STOCK_TRANSFER"},
                    "id": {"type": "string"}
                },
                "required": ["object_type", "id"]
            }),
            ("TX_CONVERTIBLE_ISSUANCE", {
                "object_type": "TX_CONVERTIBLE_ISSUANCE",
                "properties": {
                    "object_type": {"const": "TX_CONVERTIBLE_ISSUANCE"},
                    "id": {"type": "string"}
                },
                "required": ["object_type", "id"]
            })
        ]
        
        for object_type, schema in object_types_and_schemas:
            with self.subTest(object_type=object_type):
                # テストデータ
                test_data = {
                    "object_type": object_type,
                    "id": f"test-{object_type.lower()}-1"
                }
                
                # モックの設定
                self.mock_schema_loader.get_object_schema.return_value = schema
                self.mock_schema_loader.get_ref_resolver.return_value = Mock()
                
                # jsonschema.validateが成功するようにパッチ
                with patch('jsonschema.validate') as mock_validate:
                    mock_validate.return_value = None
                    
                    # テスト実行
                    result = self.object_validator.validate_object(test_data)
                    
                    # 検証
                    self.assertTrue(result.is_valid)
                    self.assertEqual(len(result.errors), 0)
    
    def test_validate_complex_nested_object(self):
        """複雑にネストしたオブジェクトの検証"""
        complex_object = {
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "complex-issuance-1",
            "stock_class_id": "preferred-series-a",
            "securityholder_id": "institutional-investor-1",
            "share_price": {
                "amount": "5000",
                "currency_code": "JPY"
            },
            "quantity": "10000",
            "date": "2023-06-15",
            "security_id": "security-complex-1",
            "nested_data": {
                "agreement_details": {
                    "clauses": [
                        {
                            "type": "anti_dilution",
                            "description": "希薄化防止条項"
                        },
                        {
                            "type": "liquidation_preference",
                            "description": "残余財産分配優先権"
                        }
                    ]
                }
            }
        }
        
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        # jsonschema.validateが成功するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            # テスト実行
            result = self.object_validator.validate_object(complex_object)
            
            # 検証
            self.assertTrue(result.is_valid)
            self.assertEqual(len(result.errors), 0)
    
    def test_validate_empty_object(self):
        """境界値: 空のオブジェクト"""
        empty_object = {}
        
        # テスト実行
        result = self.object_validator.validate_object(empty_object)
        
        # 検証
        self.assertFalse(result.is_valid)
        self.assertIn("object_type属性が存在しません", result.errors)
    
    def test_validate_object_with_null_values(self):
        """null値を含むオブジェクトの検証"""
        object_with_nulls = {
            "object_type": "TX_STOCK_ISSUANCE",
            "id": "test-null-1",
            "stock_class_id": None,
            "securityholder_id": "holder-1",
            "share_price": None,
            "quantity": "1000",
            "date": "2023-01-01",
            "security_id": "security-1"
        }
        
        # モックの設定
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        # jsonschema.validateがnull値で失敗するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = ValidationError("None is not of type 'string'")
            
            # テスト実行
            result = self.object_validator.validate_object(object_with_nulls)
            
            # 検証
            self.assertFalse(result.is_valid)
            self.assertTrue(any("JSONスキーマ検証エラー" in error for error in result.errors))
    
    # === 新しく追加するテストメソッド ===
    
    def test_validate_objects_success(self):
        """正常系: 複数オブジェクトの一括検証成功"""
        objects = [self.valid_stock_issuance, self.valid_security_holder]
        
        # モックの設定（型安全化でObjectType型で渡される）
        def mock_get_schema(object_type):
            if str(object_type) == "TX_STOCK_ISSUANCE":
                return self.stock_issuance_schema
            elif str(object_type) == "SECURITY_HOLDER":
                return self.security_holder_schema
            return None
        
        self.mock_schema_loader.get_object_schema.side_effect = mock_get_schema
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            result = self.object_validator.validate_objects(objects)
            
            self.assertTrue(result.is_valid)
            self.assertEqual(len(result.errors), 0)
    
    def test_validate_objects_mixed_results(self):
        """異常系: 複数オブジェクトで一部失敗"""
        invalid_object = {"object_type": "INVALID_TYPE", "id": "test"}
        objects = [self.valid_stock_issuance, invalid_object]
        
        def mock_get_schema(object_type):
            if str(object_type) == "TX_STOCK_ISSUANCE":
                return self.stock_issuance_schema
            return None
        
        self.mock_schema_loader.get_object_schema.side_effect = mock_get_schema
        
        result = self.object_validator.validate_objects(objects)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Object 1:" in error for error in result.errors))
    
    def test_validate_objects_invalid_input(self):
        """異常系: 無効な入力（非配列）"""
        result = self.object_validator.validate_objects("not a list")
        
        self.assertFalse(result.is_valid)
        self.assertIn("objectsは配列である必要があります", result.errors)
    
    def test_validate_object_with_schema_success(self):
        """正常系: 指定スキーマでの検証成功"""
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            result = self.object_validator.validate_object_with_schema(
                self.valid_stock_issuance, self.stock_issuance_schema
            )
            
            self.assertTrue(result.is_valid)
            self.assertEqual(len(result.errors), 0)
    
    def test_get_object_type_success(self):
        """正常系: object_type取得成功"""
        object_type = self.object_validator.get_object_type(self.valid_stock_issuance)
        expected_object_type = ObjectType("TX_STOCK_ISSUANCE")
        self.assertEqual(object_type, expected_object_type)
    
    def test_get_object_type_missing(self):
        """正常系: object_type存在しない場合"""
        object_type = self.object_validator.get_object_type({"id": "test"})
        self.assertIsNone(object_type)
    
    def test_get_object_type_invalid_input(self):
        """正常系: 無効な入力"""
        object_type = self.object_validator.get_object_type("not a dict")
        self.assertIsNone(object_type)
    
    def test_is_valid_object_type_success(self):
        """正常系: 有効なobject_type"""
        self.mock_schema_loader.has_object_schema.return_value = True
        
        object_type = ObjectType("TX_STOCK_ISSUANCE")
        is_valid = self.object_validator.is_valid_object_type(object_type)
        self.assertTrue(is_valid)
    
    def test_is_valid_object_type_invalid(self):
        """異常系: 無効なobject_type"""
        self.mock_schema_loader.has_object_schema.return_value = False
        
        object_type = ObjectType("INVALID_TYPE")
        is_valid = self.object_validator.is_valid_object_type(object_type)
        self.assertFalse(is_valid)
    
    def test_is_valid_object_type_non_string(self):
        """異常系: ObjectTypeでないobject_type"""
        is_valid = self.object_validator.is_valid_object_type(123)
        self.assertFalse(is_valid)
    
    def test_get_supported_object_types(self):
        """正常系: サポートされているobject_typeのリスト取得"""
        # SchemaLoaderのget_object_typesが呼ばれることをモック
        self.mock_schema_loader.get_object_types.return_value = ["TX_STOCK_ISSUANCE", "SECURITY_HOLDER", "TX_STOCK_TRANSFER"]
        
        supported_types = self.object_validator.get_supported_object_types()
        
        self.assertIsInstance(supported_types, list)
        self.assertIn("TX_STOCK_ISSUANCE", supported_types)
        self.assertIn("SECURITY_HOLDER", supported_types)
        self.mock_schema_loader.get_object_types.assert_called_once()
    
    
    
    
    
    
    
    
    
    def test_get_validation_context(self):
        """正常系: 検証コンテキスト取得"""
        context = self.object_validator.get_validation_context(self.valid_stock_issuance)
        
        self.assertIsInstance(context, dict)
        expected_object_type = ObjectType("TX_STOCK_ISSUANCE")
        self.assertEqual(context["object_type"], expected_object_type)
        self.assertIn("strict_mode", context)
        self.assertIn("object_size", context)
    
    def test_format_validation_error(self):
        """正常系: 検証エラーフォーマット"""
        error = ValidationError("Test error")
        formatted = self.object_validator.format_validation_error(error, self.valid_stock_issuance)
        
        self.assertIsInstance(formatted, dict)
        self.assertIn("error_message", formatted)
        self.assertIn("error_path", formatted)
        self.assertIn("object_type", formatted)
        self.assertIn("context", formatted)
    
    def test_extract_error_path_with_path(self):
        """正常系: エラーパス抽出（パスあり）"""
        error = Mock()
        error.absolute_path = ["properties", "field1", "subfield"]
        
        path = self.object_validator.extract_error_path(error)
        self.assertEqual(path, "properties.field1.subfield")
    
    def test_extract_error_path_without_path(self):
        """正常系: エラーパス抽出（パスなし）"""
        # ValidationErrorにabsolute_pathがない場合のテスト
        error = Mock(spec=[])  # spec=[]により、absolute_path属性を持たないMockを作成
        
        path = self.object_validator.extract_error_path(error)
        self.assertEqual(path, "root")
    
    def test_get_schema_for_object_success(self):
        """正常系: オブジェクトのスキーマ取得成功 (get_object_type + _get_object_schema組み合わせ)"""
        self.mock_schema_loader.get_object_schema.return_value = self.stock_issuance_schema
        
        object_type = self.object_validator.get_object_type(self.valid_stock_issuance)
        schema = self.object_validator._get_object_schema(object_type) if object_type else None
        
        self.assertEqual(schema, self.stock_issuance_schema)
        # 型安全化でObjectType型で呼び出されることを確認
        expected_call = ObjectType("TX_STOCK_ISSUANCE")
        self.mock_schema_loader.get_object_schema.assert_called_with(expected_call)
    
    def test_get_schema_for_object_no_type(self):
        """正常系: object_typeなしの場合 (get_object_type + _get_object_schema組み合わせ)"""
        object_type = self.object_validator.get_object_type({"id": "test"})
        schema = self.object_validator._get_object_schema(object_type) if object_type else None
        self.assertIsNone(schema)
    
    def test_validate_with_ref_resolution(self):
        """正常系: $ref解決を含む検証 (validate_object_with_schemaを使用)"""
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            result = self.object_validator.validate_object_with_schema(
                self.valid_stock_issuance, self.stock_issuance_schema
            )
            
            self.assertTrue(result.is_valid)
    
    def test_get_validation_stats_initial(self):
        """正常系: 初期状態の統計情報取得"""
        stats = self.object_validator.get_validation_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["total_validations"], 0)
        self.assertEqual(stats["successful_validations"], 0)
        self.assertEqual(stats["failed_validations"], 0)
        self.assertIsInstance(stats["validation_times"], list)
        self.assertIsInstance(stats["object_type_counts"], dict)
    
    def test_reset_stats(self):
        """正常系: 統計情報リセット"""
        # 統計情報を変更
        self.object_validator.validation_stats["total_validations"] = 10
        self.object_validator.validation_stats["successful_validations"] = 8
        
        # リセット実行
        self.object_validator.reset_stats()
        
        # 確認
        stats = self.object_validator.get_validation_stats()
        self.assertEqual(stats["total_validations"], 0)
        self.assertEqual(stats["successful_validations"], 0)
    
    def test_set_strict_mode_true(self):
        """正常系: 厳密モード有効化"""
        self.object_validator.set_strict_mode(True)
        self.assertTrue(self.object_validator.is_strict_mode())
    
    def test_set_strict_mode_false(self):
        """正常系: 厳密モード無効化"""
        self.object_validator.set_strict_mode(False)
        self.assertFalse(self.object_validator.is_strict_mode())
    
    def test_set_strict_mode_truthy_values(self):
        """正常系: 真偽値変換"""
        self.object_validator.set_strict_mode("true")
        self.assertTrue(self.object_validator.is_strict_mode())
        
        self.object_validator.set_strict_mode(0)
        self.assertFalse(self.object_validator.is_strict_mode())
    
    
    
    
    
    
    def test_validate_object_type_field_success(self):
        """正常系: object_typeフィールド検証成功"""
        self.mock_schema_loader.has_object_schema.return_value = True
        
        result = self.object_validator._validate_object_type_field(self.valid_stock_issuance)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_validate_object_type_field_missing(self):
        """異常系: object_typeフィールドなし"""
        result = self.object_validator._validate_object_type_field({"id": "test"})
        
        self.assertFalse(result.is_valid)
        self.assertIn("object_type属性が存在しません", result.errors)
    
    def test_validate_object_type_field_invalid(self):
        """異常系: 無効なobject_type"""
        self.mock_schema_loader.has_object_schema.return_value = False
        
        result = self.object_validator._validate_object_type_field(
            {"object_type": "INVALID_TYPE"}
        )
        
        self.assertFalse(result.is_valid)
        self.assertIn("無効な object_type: INVALID_TYPE", result.errors)
    
    def test_execute_jsonschema_validation(self):
        """正常系: JSONスキーマ検証実行 (validate_object_with_schemaを使用)"""
        self.mock_schema_loader.get_ref_resolver.return_value = Mock()
        
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            result = self.object_validator.validate_object_with_schema(
                self.valid_stock_issuance, self.stock_issuance_schema
            )
            
            self.assertTrue(result.is_valid)
    
    def test_create_validation_context(self):
        """正常系: 検証コンテキスト作成 (get_validation_contextを使用)"""
        context = self.object_validator.get_validation_context(self.valid_stock_issuance)
        
        self.assertIsInstance(context, dict)
        expected_object_type = ObjectType("TX_STOCK_ISSUANCE")
        self.assertEqual(context["object_type"], expected_object_type)
        # schema_idを手動で追加してテスト
        context["schema_id"] = self.stock_issuance_schema.get("$id", "unknown")
        self.assertIn("schema_id", context)
    
    def test_update_validation_stats(self):
        """正常系: 検証統計情報更新"""
        initial_stats = self.object_validator.get_validation_stats()
        
        self.object_validator._update_validation_stats("TX_STOCK_ISSUANCE", True, 0.1)
        
        updated_stats = self.object_validator.get_validation_stats()
        
        self.assertEqual(updated_stats["total_validations"], initial_stats["total_validations"] + 1)
        self.assertEqual(updated_stats["successful_validations"], initial_stats["successful_validations"] + 1)
        self.assertIn(0.1, updated_stats["validation_times"])
        self.assertEqual(updated_stats["object_type_counts"]["TX_STOCK_ISSUANCE"], 1)
    
    def test_str_representation(self):
        """正常系: 文字列表現"""
        str_repr = str(self.object_validator)
        
        self.assertIsInstance(str_repr, str)
        self.assertIn("ObjectValidator", str_repr)
        self.assertIn("strict_mode", str_repr)
    
    def test_repr_representation(self):
        """正常系: デバッグ用文字列表現"""
        repr_str = repr(self.object_validator)
        
        self.assertIsInstance(repr_str, str)
        self.assertIn("ObjectValidator", repr_str)
        self.assertIn("schema_loader", repr_str)
        self.assertIn("strict_mode", repr_str)


if __name__ == '__main__':
    unittest.main()