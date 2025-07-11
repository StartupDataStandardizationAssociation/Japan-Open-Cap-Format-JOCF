#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSONバリデーター用のカスタム例外クラス群

バリデーション処理で発生する様々なエラーの分類と構造化エラー情報を提供します。
"""

from typing import Any, Optional, List, Dict


class JSONValidatorError(Exception):
    """JSONバリデーターの基底例外クラス"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Args:
            message (str): エラーメッセージ
            details (Dict[str, Any], optional): 詳細な情報
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(JSONValidatorError):
    """検証処理全般のエラー"""

    def __init__(
        self,
        message: str,
        field_path: Optional[str] = None,
        expected: Optional[str] = None,
        actual: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            field_path (str, optional): エラーが発生したフィールドのパス
            expected (str, optional): 期待される値
            actual (str, optional): 実際の値
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, details)
        self.field_path = field_path
        self.expected = expected
        self.actual = actual


class SchemaError(JSONValidatorError):
    """スキーマ関連のエラー"""

    def __init__(
        self,
        message: str,
        schema_path: Optional[str] = None,
        schema_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            schema_path (str, optional): 問題のあるスキーマファイルのパス
            schema_type (str, optional): スキーマの種類（file_type, object_type等）
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, details)
        self.schema_path = schema_path
        self.schema_type = schema_type


class FileValidationError(ValidationError):
    """ファイル検証のエラー"""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        file_type: Optional[str] = None,
        line_number: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            file_path (str, optional): 検証対象ファイルのパス
            file_type (str, optional): ファイルタイプ
            line_number (int, optional): エラーが発生した行番号
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, details=details)
        self.file_path = file_path
        self.file_type = file_type
        self.line_number = line_number


class ObjectValidationError(ValidationError):
    """オブジェクト検証のエラー"""

    def __init__(
        self,
        message: str,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
        field_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            object_type (str, optional): オブジェクトタイプ
            object_id (str, optional): オブジェクトID
            field_path (str, optional): エラーが発生したフィールドのパス
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, field_path=field_path, details=details)
        self.object_type = object_type
        self.object_id = object_id


class ConfigError(JSONValidatorError):
    """設定関連のエラー"""

    def __init__(
        self,
        message: str,
        config_path: Optional[str] = None,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            config_path (str, optional): 設定ファイルのパス
            config_key (str, optional): 問題のある設定キー
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, details)
        self.config_path = config_path
        self.config_key = config_key


class SchemaLoadError(SchemaError):
    """スキーマ読み込みのエラー"""

    def __init__(
        self,
        message: str,
        schema_path: Optional[str] = None,
        parse_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            schema_path (str, optional): 読み込みに失敗したスキーマファイルのパス
            parse_error (Exception, optional): 元の解析エラー
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, schema_path=schema_path, details=details)
        self.parse_error = parse_error


class SchemaNotFoundError(SchemaError):
    """スキーマが見つからないエラー"""

    def __init__(
        self,
        message: str,
        schema_identifier: Optional[str] = None,
        schema_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            schema_identifier (str, optional): 見つからないスキーマの識別子
            schema_type (str, optional): スキーマの種類
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, schema_type=schema_type, details=details)
        self.schema_identifier = schema_identifier


class RefResolutionError(SchemaError):
    """$ref解決のエラー"""

    def __init__(
        self,
        message: str,
        ref_uri: Optional[str] = None,
        context_schema: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            ref_uri (str, optional): 解決に失敗した$refのURI
            context_schema (str, optional): エラーが発生したスキーマのコンテキスト
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, details=details)
        self.ref_uri = ref_uri
        self.context_schema = context_schema


class PerformanceError(JSONValidatorError):
    """パフォーマンス関連のエラー"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        elapsed_time: Optional[float] = None,
        threshold: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): エラーメッセージ
            operation (str, optional): 実行していた操作
            elapsed_time (float, optional): 実際の実行時間
            threshold (float, optional): 許容される閾値
            details (Dict[str, Any], optional): 追加の詳細情報
        """
        super().__init__(message, details)
        self.operation = operation
        self.elapsed_time = elapsed_time
        self.threshold = threshold


def format_validation_error(error: ValidationError) -> Dict[str, Any]:
    """
    ValidationErrorを構造化された辞書形式に変換

    Args:
        error (ValidationError): 変換するエラー

    Returns:
        Dict[str, Any]: 構造化されたエラー情報
    """
    raise NotImplementedError("format_validation_error() is not implemented yet")


def collect_validation_errors(errors: List[Exception]) -> Dict[str, Any]:
    """
    複数の検証エラーを集約して構造化された形式に変換

    Args:
        errors (List[Exception]): エラーのリスト

    Returns:
        Dict[str, Any]: 集約されたエラー情報
    """
    raise NotImplementedError("collect_validation_errors() is not implemented yet")
