#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSONバリデーターメインクラス

JOCFファイルの統合検証を行うメインクラスです。
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from .config_manager import ConfigManager
from .schema_loader import SchemaLoader
from .file_validator import FileValidator
from .validation_result import ValidationResult, AggregatedValidationResult
from .exceptions import (
    JSONValidatorError, ValidationError, FileValidationError, 
    ConfigError, SchemaLoadError
)


class JSONValidator:
    """
    JSONバリデーターメインクラス
    
    設定管理、スキーマ読み込み、ファイル検証、オブジェクト検証を統合し、
    エンドツーエンドの検証処理を提供します。
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        JSONバリデーターの初期化
        
        Args:
            config_path (str, optional): 設定ファイルのパス
        """
        # 各コンポーネントを初期化
        self.config_manager = ConfigManager(config_path)
        self.schema_loader = SchemaLoader(self.config_manager)
        self.file_validator = FileValidator(self.schema_loader)
        # ObjectValidatorはFileValidatorが内部で持つため、ここでは不要
    
    def validate(self, file_path: str) -> ValidationResult:
        """
        単一ファイルの検証を実行
        
        Args:
            file_path (str): 検証対象ファイルのパス
            
        Returns:
            ValidationResult: 検証結果
        """
        try:
            # ファイルパスの検証
            self._validate_file_path(file_path)
            
            # JSONファイルの読み込み
            data = self._load_json_file(file_path)
            
            # FileValidatorが全ての検証を担当（ファイル検証 + items配列のオブジェクト検証）
            return self.file_validator.validate_file(data)
            
        except FileValidationError as e:
            return ValidationResult(is_valid=False, errors=[str(e)])
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[f"予期しないエラー: {str(e)}"])
    
    def validate_multiple(self, file_paths: List[str]) -> AggregatedValidationResult:
        """
        複数ファイルの一括検証を実行
        
        Args:
            file_paths (List[str]): 検証対象ファイルのパスリスト
            
        Returns:
            AggregatedValidationResult: 集約された検証結果
        """
        raise NotImplementedError("JSONValidator.validate_multiple() is not implemented yet")
    
    def validate_directory(self, directory_path: str, 
                         pattern: str = "*.jocf.json") -> AggregatedValidationResult:
        """
        ディレクトリ内のファイルを一括検証
        
        Args:
            directory_path (str): 検証対象ディレクトリのパス
            pattern (str): ファイル名パターン
            
        Returns:
            AggregatedValidationResult: 集約された検証結果
        """
        raise NotImplementedError("JSONValidator.validate_directory() is not implemented yet")
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        JSONファイルを読み込む（内部メソッド）
        
        Args:
            file_path (str): ファイルパス
            
        Returns:
            Dict[str, Any]: 読み込まれたJSONデータ
            
        Raises:
            FileValidationError: ファイルの読み込みに失敗した場合
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileValidationError(f"ファイルが存在しません: {file_path}")
        except json.JSONDecodeError as e:
            raise FileValidationError(f"無効なJSON形式: {e}")
        except Exception as e:
            raise FileValidationError(f"ファイル読み込みエラー: {e}")
    
    def _validate_file_path(self, file_path: str) -> None:
        """
        ファイルパスの妥当性を検証（内部メソッド）
        
        Args:
            file_path (str): 検証するファイルパス
            
        Raises:
            FileValidationError: ファイルパスが無効な場合
        """
        # 最小限の実装：ファイルパスの基本的な検証
        if not file_path or not file_path.strip():
            raise FileValidationError("ファイルパスが空です")
        
        if not Path(file_path).exists():
            raise FileValidationError(f"ファイルが存在しません: {file_path}")
        
    def __str__(self) -> str:
        """
        文字列表現を返す
        
        Returns:
            str: JSONバリデーターの文字列表現
        """
        return f"JSONValidator(config_path={self.config_manager.get_config_file_path()})"
    
    def __repr__(self) -> str:
        """
        デバッグ用の文字列表現を返す
        
        Returns:
            str: デバッグ用の文字列表現
        """
        return f"JSONValidator(config_manager={repr(self.config_manager)})"
