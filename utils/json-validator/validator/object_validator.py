#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
オブジェクトバリデータークラス

個別のJSONオブジェクトのスキーマ検証を行うクラスです。
"""

import logging
import time
import jsonschema
from typing import Dict, Any, Optional, List, Union, Type
from jsonschema import ValidationError, RefResolver
from .schema_loader import SchemaLoader
from .validation_result import ValidationResult
from .exceptions import ObjectValidationError, SchemaNotFoundError, RefResolutionError
from .types import ObjectType


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
        
        # Logger の初期化
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info("ObjectValidatorを初期化しました")
    
    def validate_object(self, object_data: Dict[str, Any]) -> ValidationResult:
        """
        オブジェクトの検証を実行
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            
        Returns:
            ValidationResult: 検証結果
        """
        start_time = time.time()
        self.logger.info("オブジェクト検証を開始します")
        self.logger.debug(f"検証対象オブジェクト: {object_data}")
        
        result = ValidationResult()
        
        # object_type属性の確認
        self.logger.debug("object_type属性の検証を開始します")
        object_type_result = self._validate_object_type_field(object_data)
        if not object_type_result.is_valid:
            self.logger.warning(f"object_type属性の検証に失敗しました: {object_type_result.errors}")
            for error in object_type_result.errors:
                result.add_error(error)
            return result
        
        object_type_obj = self.get_object_type(object_data)
        if not object_type_obj:
            error_msg = "有効なobject_typeを取得できませんでした"
            self.logger.error(error_msg)
            result.add_error(error_msg)
            return result
        
        self.logger.debug(f"object_type取得完了: {object_type_obj}")
        
        # スキーマの取得
        self.logger.debug(f"object_type '{object_type_obj}' のスキーマを取得中")
        schema = self._get_object_schema(object_type_obj)
        if not schema:
            error_msg = f"object_type '{object_type_obj}' に対応するスキーマが見つかりません"
            self.logger.error(error_msg)
            result.add_error(error_msg)
            return result
        
        # jsonschemaによる検証
        self.logger.debug("JSONSchemaによる検証を開始します")
        validation_result = self._validate_with_jsonschema(object_data, schema)
        if not validation_result.is_valid:
            self.logger.warning(f"JSONSchema検証でエラーが発生しました: {validation_result.errors}")
            for error in validation_result.errors:
                result.add_error(error)
        
        # 統計情報の更新
        validation_time = time.time() - start_time
        self._update_validation_stats(object_type_obj, result.is_valid, validation_time)
        
        if result.is_valid:
            self.logger.info(f"オブジェクト検証が正常に完了しました (object_type: {object_type_obj}, 検証時間: {validation_time:.3f}秒)")
        else:
            self.logger.warning(f"オブジェクト検証が失敗しました (object_type: {object_type_obj}, エラー数: {len(result.errors)}, 検証時間: {validation_time:.3f}秒)")
        
        return result
    
    def validate_objects(self, objects: List[Dict[str, Any]]) -> ValidationResult:
        """
        複数のオブジェクトを一括検証
        
        Args:
            objects (List[Dict[str, Any]]): 検証対象のオブジェクトリスト
            
        Returns:
            ValidationResult: 集約された検証結果
        """
        start_time = time.time()
        self.logger.info(f"複数オブジェクトの一括検証を開始します (対象件数: {len(objects) if isinstance(objects, list) else 'N/A'})")
        
        result = ValidationResult()
        if not isinstance(objects, list):
            error_msg = "objectsは配列である必要があります"
            self.logger.error(error_msg)
            result.add_error(error_msg)
            return result
        
        total_objects = len(objects)
        successful_count = 0
        failed_count = 0
        
        for i, obj in enumerate(objects):
            self.logger.debug(f"オブジェクト {i+1}/{total_objects} の検証を開始")
            obj_result = self.validate_object(obj)
            if not obj_result.is_valid:
                failed_count += 1
                self.logger.debug(f"オブジェクト {i+1} の検証が失敗しました")
                for error in obj_result.errors:
                    result.add_error(f"Object {i}: {error}")
            else:
                successful_count += 1
                self.logger.debug(f"オブジェクト {i+1} の検証が成功しました")
        
        validation_time = time.time() - start_time
        
        if result.is_valid:
            self.logger.info(f"一括検証が正常に完了しました (成功: {successful_count}, 失敗: {failed_count}, 検証時間: {validation_time:.3f}秒)")
        else:
            self.logger.warning(f"一括検証でエラーが発生しました (成功: {successful_count}, 失敗: {failed_count}, 検証時間: {validation_time:.3f}秒)")
        
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
        return self._validate_with_jsonschema(object_data, schema)
    
    def get_object_type(self, object_data: Dict[str, Any]) -> Optional[ObjectType]:
        """
        オブジェクトからobject_typeを取得
        
        Args:
            object_data (Dict[str, Any]): 対象オブジェクト
            
        Returns:
            Optional[ObjectType]: object_type。見つからない場合はNone
        """
        if not isinstance(object_data, dict):
            return None
        
        object_type_str = object_data.get("object_type")
        if object_type_str is None:
            return None
        
        try:
            return ObjectType(object_type_str)
        except (TypeError, ValueError):
            # 無効な文字列の場合はNoneを返す
            return None
    
    def is_valid_object_type(self, object_type: ObjectType) -> bool:
        """
        object_typeが有効かどうかを確認
        
        Args:
            object_type (ObjectType): 確認するobject_type
            
        Returns:
            bool: 有効な場合True
        """
        if not isinstance(object_type, ObjectType):
            return False
        return self.schema_loader.has_object_schema(object_type)
    
    def get_supported_object_types(self) -> List[str]:
        """
        サポートされているobject_typeのリストを取得
        
        Returns:
            List[str]: サポートされているobject_typeのリスト
        """
        object_types = self.schema_loader.get_object_types()
        return [str(obj_type) for obj_type in object_types]
    
    
    
    
    
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
    
    
    
    
    def _validate_object_type_field(self, object_data: Dict[str, Any]) -> ValidationResult:
        """
        object_typeフィールドの検証（内部メソッド）
        
        Args:
            object_data (Dict[str, Any]): 検証対象のオブジェクト
            
        Returns:
            ValidationResult: 検証結果
        """
        self.logger.debug("object_typeフィールドの検証を開始します")
        result = ValidationResult()
        
        if "object_type" not in object_data:
            error_msg = "object_type属性が存在しません"
            self.logger.warning(error_msg)
            result.add_error(error_msg)
            return result
        
        object_type = object_data["object_type"]
        self.logger.debug(f"object_type値: {object_type}")
        
        if not isinstance(object_type, str):
            error_msg = "object_type属性は文字列である必要があります"
            self.logger.warning(f"{error_msg} (実際の型: {type(object_type).__name__})")
            result.add_error(error_msg)
            return result
        
        try:
            object_type_obj = ObjectType(object_type)
            if not self.is_valid_object_type(object_type_obj):
                error_msg = f"無効な object_type: {object_type}"
                self.logger.warning(error_msg)
                result.add_error(error_msg)
            else:
                self.logger.debug(f"object_type検証成功: {object_type}")
        except (TypeError, ValueError) as e:
            error_msg = f"無効な object_type: {object_type}"
            self.logger.warning(f"{error_msg} (例外: {str(e)})")
            result.add_error(error_msg)
        
        return result
    
    
    
    def _update_validation_stats(self, object_type: ObjectType, is_valid: bool, 
                               validation_time: float) -> None:
        """
        検証統計情報を更新（内部メソッド）
        
        Args:
            object_type (ObjectType): オブジェクトタイプ
            is_valid (bool): 検証結果
            validation_time (float): 検証時間
        """
        self.logger.debug(f"統計情報を更新します (object_type: {object_type}, 結果: {'成功' if is_valid else '失敗'}, 時間: {validation_time:.3f}秒)")
        
        self.validation_stats["total_validations"] = self.validation_stats["total_validations"] + 1
        if is_valid:
            self.validation_stats["successful_validations"] = self.validation_stats["successful_validations"] + 1
        else:
            self.validation_stats["failed_validations"] = self.validation_stats["failed_validations"] + 1
        
        self.validation_stats["validation_times"].append(validation_time)
        
        object_type_str = str(object_type)
        if object_type_str not in self.validation_stats["object_type_counts"]:
            self.validation_stats["object_type_counts"][object_type_str] = 0
        self.validation_stats["object_type_counts"][object_type_str] = self.validation_stats["object_type_counts"][object_type_str] + 1
        
        # 統計情報のサマリーをDEBUGレベルでログ出力
        total = self.validation_stats["total_validations"]
        success = self.validation_stats["successful_validations"]
        failed = self.validation_stats["failed_validations"]
        self.logger.debug(f"統計更新完了 - 総計: {total}, 成功: {success}, 失敗: {failed}, 成功率: {(success/total*100):.1f}%" if total > 0 else "統計更新完了 - 総計: 0")
    
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
    
    def _get_object_schema(self, object_type: ObjectType) -> Optional[Dict[str, Any]]:
        """object_typeに対応するスキーマを取得"""
        self.logger.debug(f"object_type '{object_type}' のスキーマ取得を開始します")
        
        schema = self.schema_loader.get_object_schema(object_type)
        
        if schema:
            self.logger.debug(f"スキーマ取得成功: {schema.get('$id', 'N/A')} (object_type: {object_type})")
        else:
            self.logger.warning(f"スキーマが見つかりませんでした: object_type '{object_type}'")
        
        return schema
    
    def _validate_with_jsonschema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """jsonschemaを使った検証"""
        self.logger.debug("JSONSchema検証処理を開始します")
        self.logger.debug(f"使用するスキーマID: {schema.get('$id', 'N/A')}")
        
        result = ValidationResult()
        try:
            resolver = self.schema_loader.get_ref_resolver()
            self.logger.debug("RefResolverを取得しました")
            
            # 検証実行
            jsonschema.validate(data, schema, resolver=resolver)
            self.logger.debug("JSONSchema検証が成功しました")
            
        except ValidationError as e:
            error_msg = f"JSONスキーマ検証エラー: {str(e)}"
            self.logger.warning(f"{error_msg} (パス: {'.'.join(str(x) for x in e.absolute_path) if e.absolute_path else 'root'})")
            result.add_error(error_msg)
            
        except jsonschema.RefResolutionError as e:
            error_msg = f"JSONスキーマ検証エラー: {str(e)}"
            self.logger.error(f"スキーマ参照解決エラー: {error_msg}")
            result.add_error(error_msg)
            
        except jsonschema.SchemaError as e:
            error_msg = f"JSONスキーマ検証エラー: {str(e)}"
            self.logger.error(f"スキーマ定義エラー: {error_msg}")
            result.add_error(error_msg)
            
        except TypeError as e:
            # jsonschemaライブラリ内部でのRef解決エラー（Mockオブジェクトの問題など）
            error_msg = f"JSONスキーマ検証エラー: {str(e)}"
            self.logger.error(f"型エラー: {error_msg}")
            result.add_error(error_msg)
            
        except (ValueError, AttributeError) as e:
            # jsonschemaライブラリで発生する可能性のあるその他のエラー
            error_msg = f"JSONスキーマ検証エラー: {str(e)}"
            self.logger.error(f"検証処理エラー: {error_msg}")
            result.add_error(error_msg)
            
        return result
    
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