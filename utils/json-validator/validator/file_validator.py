#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイルバリデータークラス

JOCFファイル全体の構造検証を行うクラスです。
"""

from typing import Dict, Any, Optional, List, Union
from .schema_loader import SchemaLoader
from .object_validator import ObjectValidator
from .validation_result import ValidationResult
from .exceptions import FileValidationError, SchemaNotFoundError


class FileValidator:
    """
    ファイルバリデータークラス
    
    JOCFファイルのfile_type検証、必須属性チェック、
    items配列の各要素の検証を行います。
    """
    
    def __init__(self, schema_loader: SchemaLoader):
        """
        ファイルバリデーターの初期化
        
        Args:
            schema_loader (SchemaLoader): スキーマローダーインスタンス
        """
        import logging
        self.schema_loader = schema_loader
        self.object_validator = ObjectValidator(schema_loader)  # 要求事項4対応
        self.logger = logging.getLogger(__name__)
    
    def validate_file(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        ファイル全体の検証を実行
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        
        # file_type検証
        if not self._validate_file_type(file_data):
            result.add_error("file_type属性が無効です")
            return result
        
        # スキーマ取得
        file_type = file_data.get("file_type")
        schema = self.schema_loader.get_file_schema(file_type)
        if not schema:
            result.add_error(f"file_type '{file_type}' に対応するスキーマが見つかりません")
            return result
        
        # 必須属性チェック
        if not self._validate_required_attributes(file_data, schema):
            result.add_error("必須属性が不足しています")
            return result
        
        # items配列の検証
        items_validation_result = self._validate_items_array_detailed(file_data, schema)
        if not items_validation_result.is_valid:
            for error in items_validation_result.errors:
                result.add_error(error)
            return result
        
        # その他属性の検証
        if not self._validate_other_attributes(file_data, schema):
            result.add_error("その他属性の検証に失敗しました")
            return result
        
        return result
    
    def validate_file_structure(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        ファイルの基本構造を検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_file_structure() is not implemented yet")
    
    def validate_file_type(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        file_type属性の検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_file_type() is not implemented yet")
    
    def validate_required_attributes(self, file_data: Dict[str, Any], 
                                   schema: Dict[str, Any]) -> ValidationResult:
        """
        必須属性の存在を検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_required_attributes() is not implemented yet")
    
    def validate_items_array(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        items配列の検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_items_array() is not implemented yet")
    
    def validate_items_structure(self, items: List[Dict[str, Any]]) -> ValidationResult:
        """
        items配列の構造を検証
        
        Args:
            items (List[Dict[str, Any]]): 検証対象のitemsリスト
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_items_structure() is not implemented yet")
    
    def validate_items_objects(self, items: List[Dict[str, Any]]) -> ValidationResult:
        """
        items配列の各オブジェクトを検証
        
        Args:
            items (List[Dict[str, Any]]): 検証対象のitemsリスト
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_items_objects() is not implemented yet")
    
    def validate_file_metadata(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        ファイルメタデータの検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_file_metadata() is not implemented yet")
    
    def validate_file_with_schema(self, file_data: Dict[str, Any], 
                                schema: Dict[str, Any]) -> ValidationResult:
        """
        指定されたスキーマでファイルを検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_file_with_schema() is not implemented yet")
    
    def get_file_type(self, file_data: Dict[str, Any]) -> Optional[str]:
        """
        ファイルからfile_typeを取得
        
        Args:
            file_data (Dict[str, Any]): 対象ファイルデータ
            
        Returns:
            Optional[str]: file_type。見つからない場合はNone
        """
        raise NotImplementedError("FileValidator.get_file_type() is not implemented yet")
    
    def is_valid_file_type(self, file_type: str) -> bool:
        """
        file_typeが有効かどうかを確認
        
        Args:
            file_type (str): 確認するfile_type
            
        Returns:
            bool: 有効な場合True
        """
        raise NotImplementedError("FileValidator.is_valid_file_type() is not implemented yet")
    
    def get_supported_file_types(self) -> List[str]:
        """
        サポートされているfile_typeのリストを取得
        
        Returns:
            List[str]: サポートされているfile_typeのリスト
        """
        raise NotImplementedError("FileValidator.get_supported_file_types() is not implemented yet")
    
    def get_items_count(self, file_data: Dict[str, Any]) -> int:
        """
        items配列の要素数を取得
        
        Args:
            file_data (Dict[str, Any]): 対象ファイルデータ
            
        Returns:
            int: items配列の要素数
        """
        raise NotImplementedError("FileValidator.get_items_count() is not implemented yet")
    
    def get_items_object_types(self, file_data: Dict[str, Any]) -> List[str]:
        """
        items配列に含まれるobject_typeのリストを取得
        
        Args:
            file_data (Dict[str, Any]): 対象ファイルデータ
            
        Returns:
            List[str]: object_typeのリスト
        """
        raise NotImplementedError("FileValidator.get_items_object_types() is not implemented yet")
    
    def validate_file_consistency(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        ファイル内の一貫性を検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_file_consistency() is not implemented yet")
    
    def validate_cross_references(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        ファイル内のクロスリファレンスを検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_cross_references() is not implemented yet")
    
    def validate_business_rules(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        ビジネスルールの検証
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator.validate_business_rules() is not implemented yet")
    
    def get_validation_context(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        検証コンテキストを取得
        
        Args:
            file_data (Dict[str, Any]): 対象ファイルデータ
            
        Returns:
            Dict[str, Any]: 検証コンテキスト情報
        """
        raise NotImplementedError("FileValidator.get_validation_context() is not implemented yet")
    
    def get_file_summary(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ファイルの要約情報を取得
        
        Args:
            file_data (Dict[str, Any]): 対象ファイルデータ
            
        Returns:
            Dict[str, Any]: ファイルの要約情報
        """
        raise NotImplementedError("FileValidator.get_file_summary() is not implemented yet")
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        検証統計情報を取得
        
        Returns:
            Dict[str, Any]: 検証統計情報
        """
        raise NotImplementedError("FileValidator.get_validation_stats() is not implemented yet")
    
    def reset_stats(self) -> None:
        """
        検証統計情報をリセット
        """
        raise NotImplementedError("FileValidator.reset_stats() is not implemented yet")
    
    def set_validation_options(self, options: Dict[str, Any]) -> None:
        """
        検証オプションを設定
        
        Args:
            options (Dict[str, Any]): 検証オプション
        """
        raise NotImplementedError("FileValidator.set_validation_options() is not implemented yet")
    
    def get_validation_options(self) -> Dict[str, Any]:
        """
        現在の検証オプションを取得
        
        Returns:
            Dict[str, Any]: 検証オプション
        """
        raise NotImplementedError("FileValidator.get_validation_options() is not implemented yet")
    
    def add_custom_rule(self, rule_name: str, rule_func: callable) -> None:
        """
        カスタム検証ルールを追加
        
        Args:
            rule_name (str): ルール名
            rule_func (callable): ルール関数
        """
        raise NotImplementedError("FileValidator.add_custom_rule() is not implemented yet")
    
    def remove_custom_rule(self, rule_name: str) -> None:
        """
        カスタム検証ルールを削除
        
        Args:
            rule_name (str): 削除するルール名
        """
        raise NotImplementedError("FileValidator.remove_custom_rule() is not implemented yet")
    
    def get_custom_rules(self) -> List[str]:
        """
        登録されているカスタムルールのリストを取得
        
        Returns:
            List[str]: カスタムルール名のリスト
        """
        raise NotImplementedError("FileValidator.get_custom_rules() is not implemented yet")
    
    def _validate_file_type(self, file_data: Dict[str, Any]) -> bool:
        """
        file_type属性の検証（内部メソッド）
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            bool: 検証結果
        """
        return "file_type" in file_data and isinstance(file_data["file_type"], str)
    
    def _validate_required_attributes(self, file_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        必須属性チェック（内部メソッド）
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            bool: 検証結果
        """
        required_attrs = schema.get("required", [])
        return all(attr in file_data for attr in required_attrs)
    
    def _validate_items_array(self, file_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        items配列の検証（内部メソッド）
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            bool: 検証結果
        """
        # Note: schema is available for future enhancements
        if "items" not in file_data:
            return False
        
        items = file_data["items"]
        if not isinstance(items, list):
            return False
        
        # 各要素にobject_typeが存在するかチェック
        for item in items:
            if not isinstance(item, dict) or "object_type" not in item:
                return False
        
        # 要求事項3: items配列の型チェック（許可されたobject_typeかどうか）
        if not self._validate_items_object_types(file_data, schema):
            return False
        
        return True
    
    def _validate_items_array_detailed(self, file_data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """
        items配列の詳細検証（ValidationResultを返す）
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        
        if "items" not in file_data:
            result.add_error("items属性が存在しません")
            return result
        
        items = file_data["items"]
        if not isinstance(items, list):
            result.add_error("items属性は配列である必要があります")
            return result
        
        # 各要素にobject_typeが存在するかチェック
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                result.add_error(f"items[{i}]はオブジェクトである必要があります")
                continue
            if "object_type" not in item:
                result.add_error(f"items[{i}]にobject_type属性が存在しません")
                continue
        
        # 要求事項3: items配列の型チェック（許可されたobject_typeかどうか）
        object_type_result = self._validate_items_object_types_detailed(file_data, schema)
        if not object_type_result.is_valid:
            for error in object_type_result.errors:
                result.add_error(error)
        
        # 要求事項4: items配列の各要素のオブジェクト検証
        elements_result = self._validate_items_elements_detailed(file_data, schema)
        if not elements_result.is_valid:
            for error in elements_result.errors:
                result.add_error(error)
        
        return result
    
    def _validate_items_object_types(self, file_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        items配列の各要素のobject_typeが許可されているかチェック
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            bool: すべてのobject_typeが許可されている場合True
        """
        items = file_data.get("items", [])
        
        # ファイルオブジェクト.object_type_listを取得
        file_object_types = []
        for item in items:
            if isinstance(item, dict) and "object_type" in item:
                file_object_types.append(item["object_type"])
        
        # 許可スキーマ.object_type_listを取得
        allowed_object_types = self._get_allowed_object_types(schema)
        
        # ファイルオブジェクト.object_type_list ⊆ 許可スキーマ.object_type_list の確認
        for object_type in file_object_types:
            if object_type not in allowed_object_types:
                return False
        
        return True
    
    def _validate_items_object_types_detailed(self, file_data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """
        items配列の各要素のobject_typeが許可されているかの詳細チェック
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        items = file_data.get("items", [])
        
        # ファイルオブジェクト.object_type_listを取得
        file_object_types = []
        for item in items:
            if isinstance(item, dict) and "object_type" in item:
                file_object_types.append(item["object_type"])
        
        # 許可スキーマ.object_type_listを取得
        allowed_object_types = self._get_allowed_object_types(schema)
        
        # ファイルオブジェクト.object_type_list ⊆ 許可スキーマ.object_type_list の確認
        for object_type in file_object_types:
            if object_type not in allowed_object_types:
                result.add_error(f"object_type '{object_type}' は許可されていません。許可されているobject_type: {allowed_object_types}")
        
        return result
    
    def _get_allowed_object_types(self, schema: Dict[str, Any]) -> List[str]:
        """
        スキーマから許可されたobject_typeのリストを取得
        
        Args:
            schema (Dict[str, Any]): ファイルスキーマ
            
        Returns:
            List[str]: 許可されたobject_typeのリスト
        """
        allowed_types = []
        self.logger.debug(f"Getting allowed object types from schema: {schema.get('$id', 'unknown')}")
        
        # schema["properties"]["items"]["items"]["oneOf"]から$refを取得
        try:
            items_schema = schema.get("properties", {}).get("items", {}).get("items", {})
            self.logger.debug(f"Items schema structure: {items_schema}")
            
            one_of_schemas = items_schema.get("oneOf", [])
            self.logger.debug(f"Found {len(one_of_schemas)} oneOf schemas")
            
            resolver = self.schema_loader.get_ref_resolver()
            
            for i, ref_schema in enumerate(one_of_schemas):
                if "$ref" in ref_schema:
                    ref_url = ref_schema["$ref"]
                    self.logger.debug(f"Resolving $ref {i}: {ref_url}")
                    try:
                        _, resolved_schema = resolver.resolve(ref_url)
                        self.logger.debug(f"Resolved schema keys: {list(resolved_schema.keys())}")
                        
                        # object_typeはproperties.object_type.constに定義されている
                        properties = resolved_schema.get("properties", {})
                        object_type_prop = properties.get("object_type", {})
                        if "const" in object_type_prop:
                            object_type = object_type_prop["const"]
                            allowed_types.append(object_type)
                            self.logger.debug(f"Added object_type: {object_type}")
                        else:
                            self.logger.debug(f"No object_type.const found in resolved schema: {resolved_schema.get('$id', 'unknown')}")
                    except Exception as e:
                        self.logger.debug(f"Failed to resolve $ref {ref_url}: {str(e)}")
        except Exception as e:
            self.logger.debug(f"Error in _get_allowed_object_types: {str(e)}")
        
        self.logger.debug(f"Final allowed_types: {allowed_types}")
        return allowed_types
    
    def _validate_items_elements_detailed(self, file_data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """
        items配列の各要素のオブジェクト検証（要求事項4）
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()
        items = file_data.get("items", [])
        
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue  # 既に基本チェックで検出済み
            
            # ObjectValidatorで各要素を検証
            item_result = self.object_validator.validate_object(item)
            if not item_result.is_valid:
                for error in item_result.errors:
                    result.add_error(f"items[{i}]のオブジェクト検証エラー: {error}")
        
        return result
    
    def _validate_other_attributes(self, file_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        その他属性の検証（内部メソッド）
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ
            
        Returns:
            bool: 検証結果
        """
        # additionalPropertiesの設定を確認
        additional_properties = schema.get("additionalProperties", True)
        
        # additionalProperties=falseの場合、追加プロパティをチェック
        if additional_properties is False:
            # スキーマで定義されたプロパティを取得
            defined_properties = set(schema.get("properties", {}).keys())
            
            # ファイルデータのプロパティを取得
            file_properties = set(file_data.keys())
            
            # 追加プロパティがあるかチェック
            additional_props = file_properties - defined_properties
            if additional_props:
                return False
        
        return True
    
    def _validate_file_type_field(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        file_typeフィールドの検証（内部メソッド）
        
        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator._validate_file_type_field() is not implemented yet")
    
    def _validate_items_array_structure(self, items: List[Dict[str, Any]]) -> ValidationResult:
        """
        items配列の構造を検証（内部メソッド）
        
        Args:
            items (List[Dict[str, Any]]): 検証対象のitemsリスト
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator._validate_items_array_structure() is not implemented yet")
    
    def _validate_single_item(self, item: Dict[str, Any], index: int) -> ValidationResult:
        """
        単一のアイテムを検証（内部メソッド）
        
        Args:
            item (Dict[str, Any]): 検証対象のアイテム
            index (int): アイテムのインデックス
            
        Returns:
            ValidationResult: 検証結果
        """
        raise NotImplementedError("FileValidator._validate_single_item() is not implemented yet")
    
    def _get_schema_for_file_type(self, file_type: str) -> Optional[Dict[str, Any]]:
        """
        file_typeに対応するスキーマを取得（内部メソッド）
        
        Args:
            file_type (str): ファイルタイプ
            
        Returns:
            Optional[Dict[str, Any]]: 対応するスキーマ。見つからない場合はNone
        """
        raise NotImplementedError("FileValidator._get_schema_for_file_type() is not implemented yet")
    
    def _create_validation_context(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        検証コンテキストを作成（内部メソッド）
        
        Args:
            file_data (Dict[str, Any]): 対象ファイルデータ
            
        Returns:
            Dict[str, Any]: 検証コンテキスト
        """
        raise NotImplementedError("FileValidator._create_validation_context() is not implemented yet")
    
    def _update_validation_stats(self, file_type: str, items_count: int, 
                               is_valid: bool, validation_time: float) -> None:
        """
        検証統計情報を更新（内部メソッド）
        
        Args:
            file_type (str): ファイルタイプ
            items_count (int): アイテム数
            is_valid (bool): 検証結果
            validation_time (float): 検証時間
        """
        raise NotImplementedError("FileValidator._update_validation_stats() is not implemented yet")
    
    def __str__(self) -> str:
        """
        文字列表現を返す
        
        Returns:
            str: ファイルバリデーターの文字列表現
        """
        raise NotImplementedError("FileValidator.__str__() is not implemented yet")
    
    def __repr__(self) -> str:
        """
        デバッグ用の文字列表現を返す
        
        Returns:
            str: デバッグ用の文字列表現
        """
        raise NotImplementedError("FileValidator.__repr__() is not implemented yet")