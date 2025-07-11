#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイルバリデータークラス

JOCFファイル全体の構造検証を行うクラスです。
"""

from typing import Dict, Any, Optional, List
from .schema_loader import SchemaLoader
from .object_validator import ObjectValidator
from .validation_result import ValidationResult
from .exceptions import FileValidationError, SchemaNotFoundError
from .types import FileType


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
        self.object_validator = ObjectValidator(schema_loader)
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
        file_type_str = file_data.get("file_type")
        try:
            file_type = FileType(file_type_str)
            schema = self.schema_loader.get_file_schema(file_type)
        except (TypeError, ValueError):
            schema = None

        if not schema:
            result.add_error(
                f"file_type '{file_type_str}' に対応するスキーマが見つかりません"
            )
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

        # その他属性の詳細検証（object_type検証 + additionalPropertiesチェック）
        other_attributes_result = self._validate_other_attributes_detailed(
            file_data, schema
        )
        if not other_attributes_result.is_valid:
            for error in other_attributes_result.errors:
                result.add_error(error)

        return result

    def _validate_file_type(self, file_data: Dict[str, Any]) -> bool:
        """
        file_type属性の検証（内部メソッド）

        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ

        Returns:
            bool: 検証結果
        """
        return "file_type" in file_data and isinstance(file_data["file_type"], str)

    def _validate_required_attributes(
        self, file_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> bool:
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

    def _validate_items_array_detailed(
        self, file_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> ValidationResult:
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

        # items配列の型チェック（許可されたobject_typeかどうか）
        object_type_result = self._validate_items_object_types_detailed(
            file_data, schema
        )
        if not object_type_result.is_valid:
            for error in object_type_result.errors:
                result.add_error(error)

        # items配列の各要素のオブジェクト検証
        elements_result = self._validate_items_elements_detailed(file_data, schema)
        if not elements_result.is_valid:
            for error in elements_result.errors:
                result.add_error(error)

        return result

    def _validate_items_object_types_detailed(
        self, file_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> ValidationResult:
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
                result.add_error(
                    f"object_type '{object_type}' は許可されていません。許可されているobject_type: {allowed_object_types}"
                )

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
        self.logger.debug(
            f"Getting allowed object types from schema: {schema.get('$id', 'unknown')}"
        )

        try:
            items_schema = (
                schema.get("properties", {}).get("items", {}).get("items", {})
            )
            self.logger.debug(f"Items schema structure: {items_schema}")

            registry = self.schema_loader.get_registry()

            # oneOf構造をチェック（複数オブジェクトタイプ）
            one_of_schemas = items_schema.get("oneOf", [])
            if one_of_schemas:
                self.logger.debug(f"Found {len(one_of_schemas)} oneOf schemas")

                for i, ref_schema in enumerate(one_of_schemas):
                    if "$ref" in ref_schema:
                        ref_url = ref_schema["$ref"]
                        self.logger.debug(f"Resolving $ref {i}: {ref_url}")
                        object_type = self._extract_object_type_from_ref(
                            registry, ref_url
                        )
                        if object_type:
                            allowed_types.append(object_type)

            # 直接$ref構造をチェック（単一オブジェクトタイプ）
            elif "$ref" in items_schema:
                ref_url = items_schema["$ref"]
                self.logger.debug(f"Found direct $ref: {ref_url}")
                object_type = self._extract_object_type_from_ref(registry, ref_url)
                if object_type:
                    allowed_types.append(object_type)

        except Exception as e:
            self.logger.debug(f"Error in _get_allowed_object_types: {str(e)}")

        self.logger.debug(f"Final allowed_types: {allowed_types}")
        return allowed_types

    def _extract_object_type_from_ref(self, registry, ref_url: str) -> Optional[str]:
        """
        $refを解決してobject_typeを抽出する共通処理

        Args:
            registry: Registryインスタンス
            ref_url (str): 解決する$ref URL

        Returns:
            Optional[str]: 抽出されたobject_type、取得できない場合はNone
        """
        try:
            resource = registry.get_or_retrieve(ref_url)
            resolved_schema = resource.value.contents
            self.logger.debug(f"Resolved schema keys: {list(resolved_schema.keys())}")

            # object_typeはproperties.object_type.constに定義されている
            properties = resolved_schema.get("properties", {})
            object_type_prop = properties.get("object_type", {})
            if "const" in object_type_prop:
                object_type = object_type_prop["const"]
                self.logger.debug(f"Added object_type: {object_type}")
                return object_type
            else:
                self.logger.debug(
                    f"No object_type.const found in resolved schema: {resolved_schema.get('$id', 'unknown')}"
                )
                return None
        except Exception as e:
            self.logger.debug(f"Failed to resolve $ref {ref_url}: {str(e)}")
            return None

    def _validate_items_elements_detailed(
        self, file_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        items配列の各要素のオブジェクト検証

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

    def _validate_other_attributes_detailed(
        self, file_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        その他属性の詳細検証

        Args:
            file_data (Dict[str, Any]): 検証対象のファイルデータ
            schema (Dict[str, Any]): 使用するスキーマ

        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()

        # file_type、items以外の属性を取得
        excluded_attrs = {"file_type", "items"}
        other_attributes = {
            k: v for k, v in file_data.items() if k not in excluded_attrs
        }

        for attr_name, attr_value in other_attributes.items():
            # 属性がJSONオブジェクトかつobject_typeが設定されている場合
            if isinstance(attr_value, dict) and "object_type" in attr_value:
                # ObjectValidatorで検証
                attr_result = self.object_validator.validate_object(attr_value)
                if not attr_result.is_valid:
                    for error in attr_result.errors:
                        result.add_error(
                            f"{attr_name}のオブジェクト検証エラー: {error}"
                        )

        # additionalPropertiesチェック
        additional_properties = schema.get("additionalProperties", True)
        if additional_properties is False:
            # スキーマで定義されたプロパティを取得
            defined_properties = set(schema.get("properties", {}).keys())
            # ファイルデータのプロパティを取得
            file_properties = set(file_data.keys())
            # 追加プロパティがあるかチェック
            additional_props = file_properties - defined_properties
            if additional_props:
                result.add_error(
                    f"許可されていない追加プロパティが存在します: {list(additional_props)}"
                )

        return result
