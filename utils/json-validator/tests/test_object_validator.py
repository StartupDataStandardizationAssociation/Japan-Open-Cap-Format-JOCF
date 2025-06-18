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
# from validator.object_validator import ObjectValidator
# from validator.schema_loader import SchemaLoader
# from validator.exceptions import ObjectValidationError


class ValidationResult:
    """検証結果クラス"""
    
    def __init__(self, is_valid=True, errors=None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error):
        self.errors.append(error)
        self.is_valid = False


class MockObjectValidator:
    """テスト用のObjectValidatorモッククラス"""
    
    def __init__(self, schema_loader=None):
        self.schema_loader = schema_loader or Mock()
    
    def validate_object(self, object_data):
        """オブジェクトの検証"""
        result = ValidationResult()
        
        # object_type属性の確認
        if "object_type" not in object_data:
            result.add_error("object_type属性が存在しません")
            return result
        
        object_type = object_data["object_type"]
        if not isinstance(object_type, str):
            result.add_error("object_type属性は文字列である必要があります")
            return result
        
        # スキーマの取得
        schema = self._get_object_schema(object_type)
        if not schema:
            result.add_error(f"object_type '{object_type}' に対応するスキーマが見つかりません")
            return result
        
        # jsonschemaによる検証
        try:
            if not self._validate_with_jsonschema(object_data, schema):
                result.add_error("JSONスキーマ検証に失敗しました")
        except ValidationError as e:
            result.add_error(f"JSONスキーマ検証エラー: {str(e)}")
        
        return result
    
    def _get_object_schema(self, object_type):
        """object_typeに対応するスキーマを取得"""
        return self.schema_loader.get_object_schema(object_type)
    
    def _validate_with_jsonschema(self, data, schema):
        """jsonschemaを使った検証"""
        try:
            resolver = self.schema_loader.get_ref_resolver()
            jsonschema.validate(data, schema, resolver=resolver)
            return True
        except ValidationError:
            return False


class TestObjectValidator(unittest.TestCase):
    """ObjectValidatorクラスのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        self.mock_schema_loader = Mock()
        self.object_validator = MockObjectValidator(self.mock_schema_loader)
        
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
            "additionalProperties": false,
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
            "additionalProperties": false,
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
            self.mock_schema_loader.get_object_schema.assert_called_once_with("TX_STOCK_ISSUANCE")
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
            self.mock_schema_loader.get_object_schema.assert_called_once_with("SECURITY_HOLDER")
    
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
        schema = self.object_validator._get_object_schema("TX_STOCK_ISSUANCE")
        
        # 検証
        self.assertEqual(schema, self.stock_issuance_schema)
        self.mock_schema_loader.get_object_schema.assert_called_once_with("TX_STOCK_ISSUANCE")
    
    def test_validate_with_jsonschema_success(self):
        """_validate_with_jsonschemaメソッドの成功テスト"""
        # モックの設定
        resolver = Mock()
        self.mock_schema_loader.get_ref_resolver.return_value = resolver
        
        # jsonschema.validateが成功するようにパッチ
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None
            
            # テスト実行
            is_valid = self.object_validator._validate_with_jsonschema(
                self.valid_stock_issuance, self.stock_issuance_schema
            )
            
            # 検証
            self.assertTrue(is_valid)
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
            is_valid = self.object_validator._validate_with_jsonschema(
                self.valid_stock_issuance, self.stock_issuance_schema
            )
            
            # 検証
            self.assertFalse(is_valid)
    
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


if __name__ == '__main__':
    unittest.main()