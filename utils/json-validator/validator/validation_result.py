#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
検証結果クラス

JSONバリデーションの結果を構造化して管理するクラスです。
成功・失敗の状態、エラー情報を保持します。
"""

from typing import List, Optional, Dict, Any


class ValidationResult:
    """
    検証結果を管理するクラス
    
    検証の成功・失敗状態、エラーメッセージを管理します。
    """
    
    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None):
        """
        検証結果の初期化
        
        Args:
            is_valid (bool): 検証が成功したかどうか
            errors (List[str], optional): エラーメッセージのリスト
        """
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str) -> None:
        """
        エラーを追加する
        
        Args:
            error (str): エラーメッセージ
        """
        self.errors.append(error)
        self.is_valid = False
    
    def __str__(self) -> str:
        """
        文字列表現を返す
        
        Returns:
            str: 検証結果の文字列表現
        """
        if self.is_valid:
            return "ValidationResult(valid=True)"
        else:
            return f"ValidationResult(valid=False, errors={len(self.errors)})"
    
    def __repr__(self) -> str:
        """
        デバッグ用の文字列表現を返す
        
        Returns:
            str: デバッグ用の文字列表現
        """
        return f"ValidationResult(is_valid={self.is_valid}, errors={self.errors})"
    
    def __bool__(self) -> bool:
        """
        ブール値への変換（検証が成功したかどうか）
        
        Returns:
            bool: 検証が成功した場合True
        """
        return self.is_valid
    
    def get_summary(self) -> Dict[str, Any]:
        """
        エラーサマリー情報を取得
        
        Returns:
            Dict[str, Any]: エラーサマリー情報
        """
        # エラーを分類
        error_categories = {
            'object_validation_errors': 0,
            'type_check_errors': 0,
            'schema_errors': 0,
            'other_errors': 0
        }
        
        for error in self.errors:
            if 'オブジェクト検証エラー' in error:
                error_categories['object_validation_errors'] += 1
            elif 'object_type' in error and ('許可されていません' in error or '対応するスキーマが見つかりません' in error):
                error_categories['type_check_errors'] += 1
            elif 'JSONスキーマ検証エラー' in error:
                error_categories['schema_errors'] += 1
            else:
                error_categories['other_errors'] += 1
        
        return {
            'total_errors': len(self.errors),
            'error_categories': error_categories,
            'validation_success': self.is_valid
        }