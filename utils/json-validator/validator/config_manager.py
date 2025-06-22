#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理クラス

JSON設定ファイルから設定を読み込み、環境変数での上書きをサポートする
柔軟な設定管理システムです。
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from .exceptions import ConfigError


class ConfigManager:
    """
    設定管理クラス
    
    JSON設定ファイルの読み込み、環境変数による上書き、
    動的な設定リロード機能を提供します。
    
    パス解決は以下の方針で行われます：
    - 相対パスはプロジェクトルートからの相対パスとして解釈
    - 絶対パスはそのまま使用
    - パスの存在確認は設定読み込み時に実行
    """
    
    def __new__(cls, config_path: Optional[str] = None):
        instance = super(ConfigManager, cls).__new__(cls)
        # logger初期化をここで確実に行う
        instance.logger = logging.getLogger('json_validator.config_manager')
        return instance
    
    def __init__(self, config_path: Optional[str] = None):
        """
        設定管理クラスの初期化
        
        Args:
            config_path (str, optional): 設定ファイルのパス。
                                       指定されない場合はデフォルトパスを使用
        """
        self.logger = logging.getLogger('json_validator.config_manager')
        
        # プロジェクトルートの検出（最初に実行）
        self._project_root = self._detect_project_root()
        self.logger.debug(f"Project root detected: {self._project_root}")
        
        if config_path is None:
            # デフォルトパスをプロジェクトルートベースで設定
            self._config_path = self._project_root / "utils/json-validator/config/validator_config.json"
            self.logger.debug(f"Using default config path: {self._config_path}")
        else:
            self._config_path = Path(config_path)
            # 相対パスの場合は絶対パスに変換
            if not self._config_path.is_absolute():
                self._config_path = self._project_root / self._config_path
            self.logger.debug(f"Using provided config path: {self._config_path}")
        
        # 設定ファイルの存在確認
        if not self._config_path.exists():
            self.logger.error(f"Config file not found: {self._config_path}")
            raise ConfigError(f"Config file not found: {self._config_path}")
        
        # 設定辞書の初期化
        self._config: Dict[str, Any] = {}
        
        # 設定の読み込み
        try:
            self.load_config()
        except Exception as e:
            if "Invalid JSON format" in str(e) or "Permission denied" in str(e):
                raise e
            else:
                # その他のエラーは再発生
                raise
    
    def _detect_project_root(self) -> Path:
        """
        プロジェクトルートディレクトリを検出する
        
        複数の戦略を使用してプロジェクトルートを検出します：
        1. マーカーファイル（.git, pyproject.toml, setup.py, requirements.txt）の検索
        2. 固定の相対パス（フォールバック）
        
        Returns:
            Path: プロジェクトルートディレクトリの絶対パス
        """
        current_path = Path(__file__).resolve().parent
        
        # 戦略1: マーカーファイルの検索
        markers = ['.git', 'pyproject.toml', 'setup.py', 'requirements.txt', 'mkdocs.yml']
        
        for parent in [current_path] + list(current_path.parents):
            for marker in markers:
                marker_path = parent / marker
                if marker_path.exists():
                    # ログはここで直接出力（loggerがまだ初期化されていないため）
                    return parent
        
        # 戦略2: 固定の相対パス（フォールバック）
        # utils/json-validator/validator -> repository root
        fallback_root = current_path.parent.parent.parent
        if fallback_root.exists():
            return fallback_root
        
        # 最終フォールバック: 現在のディレクトリの親
        return current_path.parent
    
    def _resolve_path(self, path_str: str) -> Path:
        """
        パス文字列を絶対Pathオブジェクトに解決する
        
        Args:
            path_str (str): 解決するパス文字列
            
        Returns:
            Path: 絶対パス
        """
        path = Path(path_str)
        
        if path.is_absolute():
            self.logger.debug(f"Path is already absolute: {path}")
            return path
        else:
            # 相対パスはプロジェクトルートからの相対パスとして解釈
            resolved_path = self._project_root / path
            self.logger.debug(f"Resolved relative path {path_str} to: {resolved_path}")
            return resolved_path
    
    def _validate_path_exists(self, path: Path, path_description: str) -> None:
        """
        パスの存在を検証する
        
        Args:
            path (Path): 検証するパス
            path_description (str): パスの説明（エラーメッセージ用）
            
        Raises:
            ConfigError: パスが存在しない場合
        """
        self.logger.debug(f"Validating path exists: {path}")
        
        if not path.exists():
            error_msg = (
                f"{path_description} does not exist: {path}\n"
                f"Project root: {self._project_root}\n"
                f"Resolved from relative path in configuration"
            )
            self.logger.error(error_msg)
            raise ConfigError(error_msg)
        
        self.logger.debug(f"Path validation successful: {path}")
    
    def load_config(self) -> None:
        """
        設定ファイルを読み込む
        
        Raises:
            ConfigError: 設定ファイルの読み込みに失敗した場合
        """
        self.logger.debug(f"Loading config from: {self._config_path}")
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            self.logger.debug(f"Config loaded successfully. Keys: {list(self._config.keys())}")
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self._config_path}")
            raise ConfigError(f"Config file not found: {self._config_path}")
        except PermissionError:
            self.logger.error(f"Permission denied: {self._config_path}")
            raise ConfigError(f"Permission denied: {self._config_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format in {self._config_path}: {e}")
            raise ConfigError(f"Invalid JSON format in {self._config_path}: {e}")
    
    def reload_config(self) -> None:
        """
        設定ファイルを再読み込みする
        
        動的な設定変更に対応するため、設定ファイルを再読み込みします。
        """
        self.load_config()
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        ドット記法で設定値を取得する
        
        Args:
            key_path (str): 設定のキーパス（例: "schema.root_path"）
            default: デフォルト値
            
        Returns:
            設定値または環境変数での上書き値
        """
        self.logger.debug(f"Getting config value for key: {key_path}")
        
        if not key_path or key_path.strip() == "":
            raise ConfigError("Invalid key path: empty string")
        
        if ".." in key_path:
            raise ConfigError("Invalid key path: contains consecutive dots")
        
        # 環境変数での上書きをチェック
        env_key = f"VALIDATOR_{key_path.replace('.', '_').upper()}"
        if env_key in os.environ:
            env_value = os.environ[env_key]
            self.logger.debug(f"Using environment override for {key_path}: {env_value}")
            # 文字列が boolean っぽい場合は変換
            if env_value.lower() in ('true', 'false'):
                return env_value.lower() == 'true'
            return env_value
        
        value = self._get_nested_value(self._config, key_path)
        if value is None:
            self.logger.debug(f"Config key {key_path} not found, using default: {default}")
            return default
        
        # 環境変数プレースホルダーを解決
        resolved_value = self._resolve_environment_variables(value)
        self.logger.debug(f"Config value for {key_path}: {resolved_value}")
        return resolved_value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        設定値を動的に設定する
        
        Args:
            key_path (str): 設定のキーパス
            value: 設定する値
        """
        if not key_path or key_path.strip() == "":
            raise ConfigError("Invalid key path: empty string")
        
        if ".." in key_path:
            raise ConfigError("Invalid key path: contains consecutive dots")
        
        self._set_nested_value(self._config, key_path, value)
    
    def get_schema_config(self) -> Dict[str, Any]:
        """
        スキーマ関連の設定を取得
        
        Returns:
            Dict[str, Any]: スキーマ設定
        """
        result = self.get("schema", {})
        return result if isinstance(result, dict) else {}
    
    def get_validation_config(self) -> Dict[str, Any]:
        """
        バリデーション関連の設定を取得
        
        Returns:
            Dict[str, Any]: バリデーション設定
        """
        result = self.get("validation", {})
        return result if isinstance(result, dict) else {}
    
    def get_output_config(self) -> Dict[str, Any]:
        """
        出力関連の設定を取得
        
        Returns:
            Dict[str, Any]: 出力設定
        """
        result = self.get("output", {})
        return result if isinstance(result, dict) else {}
    
    def get_testing_config(self) -> Dict[str, Any]:
        """
        テスト関連の設定を取得
        
        Returns:
            Dict[str, Any]: テスト設定
        """
        result = self.get("testing", {})
        return result if isinstance(result, dict) else {}
    
    def get_schema_root_path(self, validate_exists: bool = False) -> Path:
        """
        スキーマのルートパスを取得
        
        Args:
            validate_exists (bool): パスの存在確認を行うかどうか
        
        Returns:
            Path: スキーマのルートパス（絶対パス）
            
        Raises:
            ConfigError: validate_exists=Trueでスキーマルートパスが存在しない場合
        """
        path_str = self.get("schema.root_path", "schema")
        resolved_path = self._resolve_path(path_str)
        self.logger.debug(f"Schema root path resolved to: {resolved_path}")
        
        if validate_exists:
            self._validate_path_exists(resolved_path, "Schema root directory")
        
        return resolved_path
    
    def get_cache_enabled(self) -> bool:
        """
        キャッシュが有効かどうかを取得
        
        Returns:
            bool: キャッシュが有効な場合True
        """
        result = self.get("schema.cache_enabled", False)
        return bool(result)
    
    def get_samples_dir(self, validate_exists: bool = False) -> Path:
        """
        サンプルディレクトリのパスを取得
        
        Args:
            validate_exists (bool): パスの存在確認を行うかどうか
        
        Returns:
            Path: サンプルディレクトリのパス（絶対パス）
            
        Raises:
            ConfigError: validate_exists=Trueでサンプルディレクトリが存在しない場合
        """
        path_str = self.get("testing.samples_dir", "samples")
        resolved_path = self._resolve_path(path_str)
        
        if validate_exists:
            self._validate_path_exists(resolved_path, "Samples directory")
        
        return resolved_path
    
    def get_log_level(self) -> str:
        """
        ログレベルを取得
        
        Returns:
            str: ログレベル
        """
        result = self.get("output.log_level", "INFO")
        return str(result)
    
    def get_project_root(self) -> Path:
        """
        プロジェクトルートディレクトリのパスを取得
        
        Returns:
            Path: プロジェクトルートディレクトリの絶対パス
        """
        return self._project_root
    
    def is_strict_mode(self) -> bool:
        """
        厳密モードが有効かどうかを取得
        
        Returns:
            bool: 厳密モードが有効な場合True
        """
        result = self.get("validation.strict_mode", True)
        return bool(result)
    
    def get_custom_schema_paths(self) -> List[Path]:
        """
        カスタムスキーマパスのリストを取得
        
        Returns:
            List[Path]: カスタムスキーマパスのリスト（絶対パス）
            
        Note:
            存在しないパスも含まれる可能性があります。
            個別の存在確認が必要な場合は呼び出し側で実行してください。
        """
        paths_list = self.get("schema.custom_paths", [])
        return [self._resolve_path(path_str) for path_str in paths_list]
    
    def get_environment_overrides(self) -> Dict[str, str]:
        """
        環境変数による設定上書きを取得
        
        Returns:
            Dict[str, str]: 環境変数の設定マッピング
        """
        overrides = {}
        for key, value in os.environ.items():
            if key.startswith('VALIDATOR_'):
                overrides[key] = value
        return overrides
    
    def validate_config(self) -> List[str]:
        """
        設定値を検証する
        
        Returns:
            List[str]: 検証エラーのリスト（空の場合は正常）
        """
        errors = []
        
        # schema.root_path の検証
        root_path = self.get("schema.root_path")
        if root_path is None:
            errors.append("schema.root_path is required")
        elif not isinstance(root_path, str) or not root_path.strip():
            errors.append("schema.root_path must be a non-empty string")
        
        # validation.max_errors_per_object の検証
        max_errors = self.get("validation.max_errors_per_object")
        if max_errors is not None and (not isinstance(max_errors, int) or max_errors < 0):
            errors.append("validation.max_errors_per_object must be a non-negative integer")
        
        return errors
    
    def validate_paths(self) -> List[str]:
        """
        設定されたパスの存在を検証する
        
        Returns:
            List[str]: パス検証エラーのリスト（空の場合は正常）
        """
        errors = []
        
        try:
            self.get_schema_root_path(validate_exists=True)
        except ConfigError as e:
            errors.append(str(e))
        
        try:
            self.get_samples_dir(validate_exists=True)
        except ConfigError as e:
            errors.append(str(e))
        
        return errors
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        全設定を辞書形式で取得
        
        Returns:
            Dict[str, Any]: 全設定の辞書
        """
        return self._config.copy()
    
    def save_config(self, output_path: Optional[str] = None) -> None:
        """
        現在の設定をファイルに保存
        
        Args:
            output_path (str, optional): 出力先パス。Noneの場合は元のファイルを上書き
        """
        target_path = Path(output_path) if output_path else self._config_path
        self.logger.debug(f"Saving config to: {target_path}")
        
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Config saved successfully to: {target_path}")
        except (PermissionError, OSError) as e:
            self.logger.error(f"Failed to save config to {target_path}: {e}")
            raise ConfigError(f"Failed to save config to {target_path}: {e}")
    
    def merge_config(self, other_config: Dict[str, Any]) -> None:
        """
        他の設定をマージする
        
        Args:
            other_config (Dict[str, Any]): マージする設定
        """
        def deep_merge(base_dict, merge_dict):
            for key, value in merge_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_merge(self._config, other_config)
    
    def reset_to_defaults(self) -> None:
        """
        設定をデフォルト値にリセット
        """
        default_config = {
            "schema": {
                "root_path": "schema",
                "cache_enabled": True
            },
            "validation": {
                "strict_mode": True,
                "max_errors_per_object": 100
            },
            "output": {
                "format": "json",
                "log_level": "INFO"
            },
            "testing": {
                "samples_dir": "samples",
                "test_data_dir": "test_data"
            }
        }
        self._config = default_config
    
    def get_config_file_path(self) -> Path:
        """
        現在使用している設定ファイルのパスを取得
        
        Returns:
            Path: 設定ファイルのパス
        """
        return self._config_path
    
    def watch_config_file(self, callback: Callable) -> None:
        """
        設定ファイルの変更を監視する
        
        Args:
            callback: 変更時に呼び出されるコールバック関数
        """
        # 現在は監視機能は未実装
        pass
    
    def stop_watching(self) -> None:
        """
        設定ファイルの監視を停止する
        """
        # 現在は監視機能は未実装
        pass
    
    def _resolve_environment_variables(self, value: Any) -> Any:
        """
        環境変数を解決する（内部メソッド）
        
        Args:
            value: 解決する値
            
        Returns:
            解決後の値
        """
        if not isinstance(value, str):
            return value
        
        # ${VAR_NAME} 形式の環境変数を置換
        def replace_env_var(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        
        return re.sub(r'\$\{([^}]+)\}', replace_env_var, value)
    
    def _get_nested_value(self, config: Dict[str, Any], key_path: str) -> Any:
        """
        ネストした辞書から値を取得する（内部メソッド）
        
        Args:
            config (Dict[str, Any]): 設定辞書
            key_path (str): キーパス
            
        Returns:
            取得した値
        """
        keys = key_path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any) -> None:
        """
        ネストした辞書に値を設定する（内部メソッド）
        
        Args:
            config (Dict[str, Any]): 設定辞書
            key_path (str): キーパス
            value: 設定する値
        """
        keys = key_path.split('.')
        current = config
        
        # 最後のキー以外を処理して、必要に応じて辞書を作成
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        # 最後のキーに値を設定
        current[keys[-1]] = value
    
    def __str__(self) -> str:
        """
        文字列表現を返す
        
        Returns:
            str: 設定の文字列表現
        """
        schema_path = self.get("schema.root_path", "N/A")
        log_level = self.get("output.log_level", "N/A")
        return f"ConfigManager(schema_path={schema_path}, log_level={log_level})"
    
    def __repr__(self) -> str:
        """
        デバッグ用の文字列表現を返す
        
        Returns:
            str: デバッグ用の文字列表現
        """
        return f"ConfigManager(config_path={self._config_path})"


# グローバルインスタンス管理
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """
    グローバル設定マネージャーインスタンスを取得
    
    Args:
        config_path (str, optional): 設定ファイルのパス
        
    Returns:
        ConfigManager: 設定管理インスタンス
    """
    global _global_config_manager
    logger = logging.getLogger('json_validator.config_manager')
    
    if _global_config_manager is None:
        logger.debug(f"Creating new global ConfigManager with path: {config_path}")
        _global_config_manager = ConfigManager(config_path)
    else:
        logger.debug("Returning existing global ConfigManager")
    
    return _global_config_manager


def reset_config_manager() -> None:
    """
    グローバル設定マネージャーインスタンスをリセット（主にテスト用）
    """
    global _global_config_manager
    _global_config_manager = None


def load_config_from_dict(config_dict: Dict[str, Any]) -> ConfigManager:
    """
    辞書から設定マネージャーを作成
    
    Args:
        config_dict (Dict[str, Any]): 設定辞書
        
    Returns:
        ConfigManager: 設定管理インスタンス
    """
    # 空のインスタンスを作成し、設定を直接設定
    cm = ConfigManager.__new__(ConfigManager)
    cm._config = config_dict.copy()
    cm._config_path = Path("<from_dict>")
    
    # loggerは既に__new__で初期化済み
    
    # プロジェクトルートの検出
    cm._project_root = cm._detect_project_root()

    # cmがConfigManagerのインスタンスであることを確認
    if not isinstance(cm, ConfigManager):
        raise TypeError("Expected an instance of ConfigManager")   
    return cm