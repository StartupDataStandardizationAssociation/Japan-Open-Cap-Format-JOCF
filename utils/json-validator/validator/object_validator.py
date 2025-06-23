#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
オブジェクトバリデータークラス

個別のJSONオブジェクトのスキーマ検証を行うクラスです。
"""

import jsonschema
from typing import Dict, Any, Optional, List, Union, Callable, Type
from jsonschema import ValidationError, RefResolver
from .schema_loader import SchemaLoader
from .validation_result import ValidationResult
from .exceptions import ObjectValidationError, SchemaNotFoundError, RefResolutionError


class ObjectValidator:
    """
    オブジェクトバリデータークラス
    
    JSONオブジェクトのobject_typeに基づいて適切なスキーマを特定し、
    jsonschema.validateを使用して完全な検証を実行します。
    """
    
    def __init__(self, schema_loader: SchemaLoader):
        """
        オブジェクトバリデーターの初期化
        
        Args:
            schema_loader (SchemaLoader): スキーマローダーインスタンス
        """
        self.schema_loader = schema_loader
        self.strict_mode = False
        self.validation_stats: Dict[str, Any] = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "validation_times": [],
            "object_type_counts": {}
        }
        self.custom_validators: Dict[str, Callable[[Any], bool]] = {}
    
    def validate_object(self, object_data: Dict[str, Any]) -> ValidationResult:
        """
        オブジェクトの検証を実行
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            
        Returns:
            ValidationResult: 検証結果
        """
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
            resolver = self.schema_loader.get_ref_resolver()
            jsonschema.validate(object_data, schema, resolver=resolver)
        except ValidationError as e:
            result.add_error(f"JSONスキーマ検証エラー: {str(e)}")
        except jsonschema.RefResolutionError as e:
            result.add_error(f"JSONスキーマ検証エラー: {str(e)}")
        except jsonschema.SchemaError as e:
            result.add_error(f"JSONスキーマ検証エラー: {str(e)}")
        except TypeError as e:
            # jsonschemaライブラリ内部でのRef解決エラー（Mockオブジェクトの問題など）
            result.add_error(f"JSONスキーマ検証エラー: {str(e)}")
        except (ValueError, AttributeError) as e:
            # jsonschemaライブラリで発生する可能性のあるその他のエラー
            result.add_error(f"JSONスキーマ検証エラー: {str(e)}")
        
        return result
    
    def validate_objects(self, objects: List[Dict[str, Any]]) -> ValidationResult:
        """
        複数のオブジェクトを一括検証
        
        Args:
            objects (List[Dict[str, Any]]): 検証対象のオブジェクトリスト
            
        Returns:
            ValidationResult: 集約された検証結果
        """
        result = ValidationResult()
        if not isinstance(objects, list):
            result.add_error("objectsは配列である必要があります")
            return result
        
        for i, obj in enumerate(objects):
            obj_result = self.validate_object(obj)
            if not obj_result.is_valid:
                for error in obj_result.errors:
                    result.add_error(f"Object {i}: {error}")
        return result
    
    def validate_object_with_schema(self, object_data: Dict[str, Any], 
                                  schema: Dict[str, Any]) -> ValidationResult:
        """
        指定されたスキーマでオブジェクトを検証
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        try:
            if not self._validate_with_jsonschema(object_data, schema):
                result.add_error("JSONスキーマ検証に失敗しました")
        except ValidationError as e:
            result.add_error(f"JSONスキーマ検証エラー: {str(e)}")
        return result
    
    def get_object_type(self, object_data: Dict[str, Any]) -> Optional[str]:
        """
        オブジェクトからobject_typeを取得
        
        Args:
            object_data (Dict[str, Any]): 対象オブジェクト
            
        Returns:
            Optional[str]: object_type。見つからない場合はNone
        """
        if not isinstance(object_data, dict):
            return None
        return object_data.get("object_type")
    
    def is_valid_object_type(self, object_type: str) -> bool:
        """
        object_typeが有効かどうかを確認
        
        Args:
            object_type (str): 確認するobject_type
            
        Returns:
            bool: 有効な場合True
        """
        if not isinstance(object_type, str):
            return False
        return self.schema_loader.has_object_schema(object_type)
    
    def get_supported_object_types(self) -> List[str]:
        """
        サポートされているobject_typeのリストを取得
        
        Returns:
            List[str]: サポートされているobject_typeのリスト
        """
        return ["TX_STOCK_ISSUANCE", "SECURITY_HOLDER", "TX_STOCK_TRANSFER", "TX_CONVERTIBLE_ISSUANCE"]
    
    def validate_object_structure(self, object_data: Dict[str, Any]) -> ValidationResult:
        """
        オブジェクトの基本構造を検証
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        if not isinstance(object_data, dict):
            result.add_error("オブジェクトは辞書型である必要があります")
        elif not object_data:
            result.add_error("オブジェクトは空であってはいけません")
        return result
    
    def validate_required_fields(self, object_data: Dict[str, Any], 
                                schema: Dict[str, Any]) -> ValidationResult:
        """
        必須フィールドの存在を検証
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in object_data:
                result.add_error(f"必須フィールド '{field}' が存在しません")
        return result
    
    def validate_field_types(self, object_data: Dict[str, Any], 
                           schema: Dict[str, Any]) -> ValidationResult:
        """
        フィールドの型を検証
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        properties = schema.get("properties", {})
        for field, value in object_data.items():
            if field in properties:
                field_schema = properties[field]
                expected_type = field_schema.get("type")
                if expected_type and not self._check_type(value, expected_type):
                    result.add_error(f"フィールド '{field}' の型が不正です")
        return result
    
    def validate_custom_constraints(self, object_data: Dict[str, Any], 
                                  schema: Dict[str, Any]) -> ValidationResult:
        """
        カスタム制約を検証
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        # カスタム制約の検証ロジック（スタブ）
        return result
    
    def get_validation_context(self, object_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        検証コンテキストを取得
        
        Args:
            object_data (Dict[str, Any]): 対象オブジェクト
            
        Returns:
            Dict[str, Any]: 検証コンテキスト情報
        """
        return {
            "object_type": self.get_object_type(object_data),
            "strict_mode": self.strict_mode,
            "object_size": len(object_data) if isinstance(object_data, dict) else 0
        }
    
    def format_validation_error(self, error: ValidationError, 
                              object_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        検証エラーをフォーマット
        
        Args:
            error (ValidationError): jsonschemaの検証エラー
            object_data (Dict[str, Any]): 対象オブジェクト
            
        Returns:
            Dict[str, Any]: フォーマットされたエラー情報
        """
        return {
            "error_message": str(error),
            "error_path": self.extract_error_path(error),
            "object_type": self.get_object_type(object_data),
            "context": self.get_validation_context(object_data)
        }
    
    def extract_error_path(self, error: ValidationError) -> str:
        """
        検証エラーからフィールドパスを抽出
        
        Args:
            error (ValidationError): jsonschemaの検証エラー
            
        Returns:
            str: エラーが発生したフィールドパス
        """
        if hasattr(error, 'absolute_path'):
            return ".".join(str(x) for x in error.absolute_path)
        return "root"
    
    def get_schema_for_object(self, object_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        オブジェクトに対応するスキーマを取得
        
        Args:
            object_data (Dict[str, Any]): 対象オブジェクト
            
        Returns:
            Optional[Dict[str, Any]]: 対応するスキーマ。見つからない場合はNone
        """
        object_type = self.get_object_type(object_data)
        if object_type:
            return self._get_object_schema(object_type)
        return None
    
    def validate_with_ref_resolution(self, object_data: Dict[str, Any], 
                                   schema: Dict[str, Any]) -> ValidationResult:
        """
        $ref解決を含む検証を実行
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        return self.validate_object_with_schema(object_data, schema)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        検証統計情報を取得
        
        Returns:
            Dict[str, Any]: 検証統計情報
        """
        return self.validation_stats.copy()
    
    def reset_stats(self) -> None:
        """
        検証統計情報をリセット
        """
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "validation_times": [],
            "object_type_counts": {}
        }
    
    def set_strict_mode(self, strict: bool) -> None:
        """
        厳密モードを設定
        
        Args:
            strict (bool): 厳密モードの有効/無効
        """
        self.strict_mode = bool(strict)
    
    def is_strict_mode(self) -> bool:
        """
        厳密モードが有効かどうかを確認
        
        Returns:
            bool: 厳密モードが有効な場合True
        """
        return self.strict_mode
    
    def add_custom_validator(self, validator_name: str, validator_func: Callable[[Any], bool]) -> None:
        """
        カスタムバリデーターを追加
        
        Args:
            validator_name (str): バリデーター名
            validator_func (callable): バリデーター関数
        """
        if not callable(validator_func):
            raise ValueError("validator_funcは呼び出し可能である必要があります")
        self.custom_validators[validator_name] = validator_func
    
    def remove_custom_validator(self, validator_name: str) -> None:
        """
        カスタムバリデーターを削除
        
        Args:
            validator_name (str): 削除するバリデーター名
        """
        if validator_name in self.custom_validators:
            del self.custom_validators[validator_name]
    
    def get_custom_validators(self) -> List[str]:
        """
        登録されているカスタムバリデーターのリストを取得
        
        Returns:
            List[str]: カスタムバリデーター名のリスト
        """
        return list(self.custom_validators.keys())
    
    def _validate_object_type_field(self, object_data: Dict[str, Any]) -> ValidationResult:
        """
        object_typeフィールドの検証（内部メソッド）
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        object_type = self.get_object_type(object_data)
        if not object_type:
            result.add_error("object_type フィールドが見つかりません")
        elif not self.is_valid_object_type(object_type):
            result.add_error(f"無効な object_type: {object_type}")
        return result
    
    def _execute_jsonschema_validation(self, object_data: Dict[str, Any], 
                                     schema: Dict[str, Any]) -> ValidationResult:
        """
        jsonschemaライブラリを使用した検証を実行（内部メソッド）
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        return self.validate_object_with_schema(object_data, schema)
    
    def _create_validation_context(self, object_data: Dict[str, Any], 
                                 schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        検証コンテキストを作成（内部メソッド）
        
        Args:
            object_data (Dict[str, Any]): 対象オブジェクト
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            Dict[str, Any]: 検証コンテキスト
        """
        context = self.get_validation_context(object_data)
        context["schema_id"] = schema.get("$id", "unknown")
        return context
    
    def _update_validation_stats(self, object_type: str, is_valid: bool, 
                               validation_time: float) -> None:
        """
        検証統計情報を更新（内部メソッド）
        
        Args:
            object_type (str): オブジェクトタイプ
            is_valid (bool): 検証結果
            validation_time (float): 検証時間
        """
        self.validation_stats["total_validations"] = self.validation_stats["total_validations"] + 1
        if is_valid:
            self.validation_stats["successful_validations"] = self.validation_stats["successful_validations"] + 1
        else:
            self.validation_stats["failed_validations"] = self.validation_stats["failed_validations"] + 1
        
        self.validation_stats["validation_times"].append(validation_time)
        
        if object_type not in self.validation_stats["object_type_counts"]:
            self.validation_stats["object_type_counts"][object_type] = 0
        self.validation_stats["object_type_counts"][object_type] = self.validation_stats["object_type_counts"][object_type] + 1
    
    def __str__(self) -> str:
        """
        文字列表現を返す
        
        Returns:
            str: オブジェクトバリデーターの文字列表現
        """
        return f"ObjectValidator(strict_mode={self.strict_mode})"
    
    def __repr__(self) -> str:
        """
        デバッグ用の文字列表現を返す
        
        Returns:
            str: デバッグ用の文字列表現
        """
        return f"ObjectValidator(schema_loader={self.schema_loader}, strict_mode={self.strict_mode})"
    
    def _get_object_schema(self, object_type: str) -> Optional[Dict[str, Any]]:
        """object_typeに対応するスキーマを取得"""
        return self.schema_loader.get_object_schema(object_type)
    
    def _validate_with_jsonschema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """jsonschemaを使った検証"""
        try:
            resolver = self.schema_loader.get_ref_resolver()
            jsonschema.validate(data, schema, resolver=resolver)
            return True
        except ValidationError:
            return False
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """型チェックのヘルパーメソッド"""
        type_mapping: Dict[str, Union[Type[Any], tuple]] = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is not None:
            return isinstance(value, expected_python_type)
        return True