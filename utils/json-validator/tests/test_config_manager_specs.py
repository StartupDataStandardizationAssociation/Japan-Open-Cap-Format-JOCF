#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigManager仕様説明用のテストコード

このテストファイルは、ConfigManagerクラスの使用方法と仕様を説明することを目的としています。
実際の使用例を通じて、各機能の動作を理解できるように構成されています。

対象クラス: validator.config_manager.ConfigManager
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from validator.config_manager import (
    ConfigManager,
    get_config_manager,
    reset_config_manager,
    load_config_from_dict,
)
from validator.exceptions import ConfigError


class TestConfigManagerBasicUsage:
    """ConfigManagerの基本的な使用方法を説明するテスト"""

    def test_basic_initialization_and_config_loading(self):
        """
        基本的な初期化と設定の読み込み

        ConfigManagerは以下の方法で初期化できます:
        1. デフォルトパス使用（config/validator_config.json）
        2. カスタムパス指定
        """
        # デフォルトパスでの初期化（実際のconfig/validator_config.jsonを使用）
        cm_default = ConfigManager()
        assert cm_default.get_config_file_path().name == "validator_config.json"

        # カスタムパスでの初期化
        sample_config = {
            "schema": {"root_path": "custom_schema"},
            "validation": {"strict_mode": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm_custom = ConfigManager(f.name)
                assert cm_custom.get("schema.root_path") == "custom_schema"
                assert cm_custom.get("validation.strict_mode") is True
            finally:
                os.unlink(f.name)

    def test_dot_notation_config_access(self):
        """
        ドット記法による設定値の取得と設定

        ConfigManagerは階層化された設定をドット記法でアクセスできます。
        例: "schema.root_path", "validation.strict_mode"
        """
        sample_config = {
            "schema": {
                "root_path": "schema",
                "cache_enabled": True,
                "nested": {"deep": {"value": "deep_config"}},
            },
            "validation": {"strict_mode": False, "max_errors_per_object": 100},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)

                # 基本的な値の取得
                assert cm.get("schema.root_path") == "schema"
                assert cm.get("validation.strict_mode") is False
                assert cm.get("validation.max_errors_per_object") == 100

                # 深い階層の値の取得
                assert cm.get("schema.nested.deep.value") == "deep_config"

                # デフォルト値の使用
                assert cm.get("nonexistent.key", "default") == "default"
                assert cm.get("nonexistent.key") is None

                # 値の設定
                cm.set("schema.root_path", "new_schema")
                assert cm.get("schema.root_path") == "new_schema"

                # 新しい階層の作成
                cm.set("new.nested.config", "new_value")
                assert cm.get("new.nested.config") == "new_value"

            finally:
                os.unlink(f.name)

    def test_configuration_sections_access(self):
        """
        設定セクションごとのアクセス方法

        ConfigManagerは設定を論理的なセクションに分けて管理します:
        - schema: スキーマ関連設定
        - validation: バリデーション関連設定
        - output: 出力関連設定
        - testing: テスト関連設定
        """
        sample_config = {
            "schema": {
                "root_path": "schema",
                "cache_enabled": True,
                "custom_paths": ["/path1", "/path2"],
            },
            "validation": {
                "strict_mode": True,
                "max_errors_per_object": 50,
                "allow_additional_properties": False,
            },
            "output": {
                "format": "json",
                "include_warnings": True,
                "log_level": "DEBUG",
            },
            "testing": {"samples_dir": "samples", "test_data_dir": "test_data"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)

                # セクション全体の取得
                schema_config = cm.get_schema_config()
                validation_config = cm.get_validation_config()
                output_config = cm.get_output_config()
                testing_config = cm.get_testing_config()

                # スキーマ設定の確認
                assert schema_config["root_path"] == "schema"
                assert schema_config["cache_enabled"] is True
                assert schema_config["custom_paths"] == ["/path1", "/path2"]

                # バリデーション設定の確認
                assert validation_config["strict_mode"] is True
                assert validation_config["max_errors_per_object"] == 50
                assert validation_config["allow_additional_properties"] is False

                # 出力設定の確認
                assert output_config["format"] == "json"
                assert output_config["include_warnings"] is True
                assert output_config["log_level"] == "DEBUG"

                # テスト設定の確認
                assert testing_config["samples_dir"] == "samples"
                assert testing_config["test_data_dir"] == "test_data"

            finally:
                os.unlink(f.name)


class TestConfigManagerTypedAccessMethods:
    """型付きアクセスメソッドの使用方法を説明するテスト"""

    def test_boolean_config_access(self):
        """
        ブール型設定値の取得

        ConfigManagerは特定の設定値に対して型安全なアクセス方法を提供します。
        """
        sample_config = {
            "schema": {"cache_enabled": True},
            "validation": {"strict_mode": False},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)

                # ブール型メソッドの使用
                cache_enabled = cm.get_cache_enabled()
                strict_mode = cm.is_strict_mode()

                assert isinstance(cache_enabled, bool)
                assert cache_enabled is True

                assert isinstance(strict_mode, bool)
                assert strict_mode is False

                # 設定が存在しない場合のデフォルト値
                cm_empty = load_config_from_dict({})
                assert isinstance(cm_empty.get_cache_enabled(), bool)
                assert isinstance(cm_empty.is_strict_mode(), bool)

            finally:
                os.unlink(f.name)

    def test_path_config_access(self):
        """
        パス型設定値の取得

        ConfigManagerはファイルパスをPathオブジェクトとして返すメソッドを提供します。
        """
        sample_config = {
            "schema": {
                "root_path": "custom_schema",
                "custom_paths": ["/absolute/path", "relative/path", "/another/path"],
            },
            "testing": {"samples_dir": "test_samples"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)

                # Pathオブジェクトとしての取得
                schema_root = cm.get_schema_root_path()
                samples_dir = cm.get_samples_dir()
                custom_paths = cm.get_custom_schema_paths()

                assert isinstance(schema_root, Path)
                assert schema_root.is_absolute()  # 絶対パスを返すことを確認
                assert (
                    schema_root.name == "custom_schema"
                )  # ディレクトリ名が正しいことを確認

                assert isinstance(samples_dir, Path)
                assert samples_dir.is_absolute()  # 絶対パスを返すことを確認
                assert (
                    samples_dir.name == "test_samples"
                )  # ディレクトリ名が正しいことを確認

                assert isinstance(custom_paths, list)
                assert len(custom_paths) == 3
                assert all(isinstance(p, Path) for p in custom_paths)
                # 絶対パスはそのまま、相対パスは絶対パスに変換される
                assert str(custom_paths[0]) == "/absolute/path"  # 絶対パス
                assert custom_paths[1].is_absolute()  # 相対パスが絶対パスに変換される
                assert custom_paths[1].name == "path"  # ディレクトリ名の確認
                assert str(custom_paths[2]) == "/another/path"  # 絶対パス

            finally:
                os.unlink(f.name)

    def test_string_config_access(self):
        """
        文字列型設定値の取得
        """
        sample_config = {"output": {"log_level": "WARNING"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)

                log_level = cm.get_log_level()
                assert isinstance(log_level, str)
                assert log_level == "WARNING"

                # デフォルト値の確認
                cm_empty = load_config_from_dict({})
                default_log_level = cm_empty.get_log_level()
                assert isinstance(default_log_level, str)
                assert default_log_level == "INFO"  # デフォルト値

            finally:
                os.unlink(f.name)


class TestConfigManagerEnvironmentVariables:
    """環境変数による設定上書き機能の説明"""

    def test_environment_variable_override_mechanism(self):
        """
        環境変数による設定上書きの仕組み

        ConfigManagerは環境変数による設定の上書きをサポートします。
        環境変数名のパターン: VALIDATOR_{設定パス}_大文字
        例: schema.root_path → VALIDATOR_SCHEMA_ROOT_PATH
        """
        sample_config = {
            "schema": {"root_path": "default_schema"},
            "validation": {"strict_mode": False},
            "output": {"log_level": "INFO"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                # 環境変数による上書きテスト
                with patch.dict(
                    "os.environ",
                    {
                        "VALIDATOR_SCHEMA_ROOT_PATH": "/override/schema",
                        "VALIDATOR_VALIDATION_STRICT_MODE": "true",
                        "VALIDATOR_OUTPUT_LOG_LEVEL": "DEBUG",
                        "OTHER_VARIABLE": "ignored",  # VALIDATOR_プレフィックスなしは無視される
                    },
                ):
                    cm = ConfigManager(f.name)

                    # 環境変数による上書きが適用されていることを確認
                    assert cm.get("schema.root_path") == "/override/schema"
                    assert (
                        cm.get("validation.strict_mode") is True
                    )  # 文字列"true"がbooleanに変換
                    assert cm.get("output.log_level") == "DEBUG"

                    # 環境変数の取得
                    env_overrides = cm.get_environment_overrides()
                    assert "VALIDATOR_SCHEMA_ROOT_PATH" in env_overrides
                    assert "VALIDATOR_VALIDATION_STRICT_MODE" in env_overrides
                    assert "VALIDATOR_OUTPUT_LOG_LEVEL" in env_overrides
                    assert (
                        "OTHER_VARIABLE" not in env_overrides
                    )  # プレフィックスなしは除外

            finally:
                os.unlink(f.name)

    def test_environment_variable_override_scope_limitation(self):
        """
        環境変数上書きの適用範囲の制限

        環境変数による上書きは get() メソッドでのみ適用され、
        get_*_config() メソッドで取得したDict[str, Any]には適用されません。
        """
        sample_config = {
            "testing": {"samples_dir": "default_samples"},
            "schema": {"root_path": "default_schema"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                with patch.dict(
                    "os.environ",
                    {
                        "VALIDATOR_TESTING_SAMPLES_DIR": "env_override_samples",
                        "VALIDATOR_SCHEMA_ROOT_PATH": "env_override_schema",
                    },
                ):
                    cm = ConfigManager(f.name)

                    # get()メソッドでは環境変数上書きが適用される
                    assert cm.get("testing.samples_dir") == "env_override_samples"
                    assert cm.get("schema.root_path") == "env_override_schema"

                    # get_*_config()で取得した辞書では環境変数上書きが適用されない
                    testing_config = cm.get_testing_config()
                    schema_config = cm.get_schema_config()

                    assert (
                        testing_config.get("samples_dir") == "default_samples"
                    )  # 元の値のまま
                    assert (
                        schema_config.get("root_path") == "default_schema"
                    )  # 元の値のまま

                    # この違いは意図的な設計：
                    # - get()は動的な環境変数適用
                    # - get_*_config()は設定ファイルの原型を返す

            finally:
                os.unlink(f.name)

    def test_environment_variable_placeholder_resolution(self):
        """
        環境変数プレースホルダーの解決

        設定値内の ${VAR_NAME} 形式のプレースホルダーは環境変数の値に置換されます。
        """
        sample_config = {
            "schema": {"root_path": "${SCHEMA_DIR}/schemas"},
            "output": {"report_dir": "${HOME}/reports/${PROJECT_NAME}"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                with patch.dict(
                    "os.environ",
                    {
                        "SCHEMA_DIR": "/app/data",
                        "HOME": "/home/user",
                        "PROJECT_NAME": "myproject",
                    },
                ):
                    cm = ConfigManager(f.name)

                    # プレースホルダーが解決されていることを確認
                    assert cm.get("schema.root_path") == "/app/data/schemas"
                    assert cm.get("output.report_dir") == "/home/user/reports/myproject"

                    # 存在しない環境変数はそのまま残る
                    cm.set("test.path", "${NONEXISTENT_VAR}/path")
                    assert cm.get("test.path") == "${NONEXISTENT_VAR}/path"

            finally:
                os.unlink(f.name)


class TestConfigManagerValidationAndErrorHandling:
    """設定検証とエラーハンドリングの説明"""

    def test_configuration_validation(self):
        """
        設定値の検証機能

        ConfigManagerは設定値の妥当性を検証する機能を提供します。
        """
        # 有効な設定
        valid_config = {
            "schema": {"root_path": "valid_schema"},
            "validation": {"max_errors_per_object": 100},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_config, f)
            f.flush()

            try:
                cm_valid = ConfigManager(f.name)
                validation_errors = cm_valid.validate_config()
                assert isinstance(validation_errors, list)
                assert len(validation_errors) == 0  # エラーなし

            finally:
                os.unlink(f.name)

        # 無効な設定
        invalid_config = {
            "schema": {"root_path": None},  # 無効な値
            "validation": {"max_errors_per_object": -1},  # 負の値
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(invalid_config, f)
            f.flush()

            try:
                cm_invalid = ConfigManager(f.name)
                validation_errors = cm_invalid.validate_config()
                assert isinstance(validation_errors, list)
                assert len(validation_errors) > 0  # エラーが存在

                # エラーメッセージの確認
                error_text = " ".join(validation_errors)
                assert "root_path" in error_text
                assert "max_errors_per_object" in error_text

            finally:
                os.unlink(f.name)

    def test_error_handling_scenarios(self):
        """
        エラーハンドリングのシナリオ

        ConfigManagerは様々なエラー状況を適切に処理します。
        """
        # 1. 存在しないファイル
        with pytest.raises(ConfigError) as exc_info:
            ConfigManager("/nonexistent/path/config.json")
        assert "Config file not found" in str(exc_info.value)

        # 2. 無効なJSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            f.flush()

            try:
                with pytest.raises(ConfigError) as exc_info:
                    ConfigManager(f.name)
                assert "Invalid JSON format" in str(exc_info.value)
            finally:
                os.unlink(f.name)

        # 3. 無効なキーパス
        cm = load_config_from_dict({"test": "value"})

        with pytest.raises(ConfigError) as exc_info:
            cm.get("")
        assert "Invalid key path" in str(exc_info.value)

        with pytest.raises(ConfigError) as exc_info:
            cm.set("key..double.dot", "value")
        assert "Invalid key path" in str(exc_info.value)


class TestConfigManagerFileOperations:
    """ファイル操作機能の説明"""

    def test_config_file_operations(self):
        """
        設定ファイルの操作（保存、再読み込み、マージ）

        ConfigManagerは設定の動的な変更と永続化をサポートします。
        """
        original_config = {
            "schema": {"root_path": "original_schema"},
            "validation": {"strict_mode": True},
        }

        # 一時ディレクトリでのテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"

            # 初期設定ファイルの作成
            with open(config_path, "w") as f:
                json.dump(original_config, f)

            cm = ConfigManager(str(config_path))

            # 1. 設定の変更
            cm.set("schema.root_path", "modified_schema")
            cm.set("output.format", "detailed_json")

            # 2. 設定の保存
            output_path = Path(temp_dir) / "modified_config.json"
            cm.save_config(str(output_path))

            # 保存された設定の確認
            with open(output_path, "r") as f:
                saved_config = json.load(f)
            assert saved_config["schema"]["root_path"] == "modified_schema"
            assert saved_config["output"]["format"] == "detailed_json"

            # 3. 設定の再読み込み
            # 元のファイルを外部から変更
            external_config = {
                "schema": {"root_path": "external_change"},
                "validation": {"strict_mode": False},
            }
            with open(config_path, "w") as f:
                json.dump(external_config, f)

            # 再読み込み
            cm.reload_config()
            assert cm.get("schema.root_path") == "external_change"
            assert cm.get("validation.strict_mode") is False

    def test_config_merging_and_reset(self):
        """
        設定のマージとリセット機能
        """
        base_config = {
            "schema": {"root_path": "base_schema", "cache_enabled": True},
            "validation": {"strict_mode": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(base_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)

                # 設定のマージ
                merge_config = {
                    "schema": {
                        "cache_enabled": False,
                        "auto_reload": True,
                    },  # 既存を上書き + 新規追加
                    "output": {"format": "json"},  # 新しいセクション
                }

                cm.merge_config(merge_config)

                # マージ結果の確認
                assert cm.get("schema.root_path") == "base_schema"  # 保持
                assert cm.get("schema.cache_enabled") is False  # 上書き
                assert cm.get("schema.auto_reload") is True  # 新規追加
                assert cm.get("validation.strict_mode") is True  # 保持
                assert cm.get("output.format") == "json"  # 新しいセクション

                # デフォルトへのリセット
                cm.reset_to_defaults()

                # デフォルト値の確認
                schema_config = cm.get_schema_config()
                validation_config = cm.get_validation_config()

                assert "root_path" in schema_config
                assert "strict_mode" in validation_config
                assert schema_config["root_path"] == "schema"  # デフォルト値
                assert validation_config["strict_mode"] is True  # デフォルト値

            finally:
                os.unlink(f.name)


class TestConfigManagerGlobalFunctions:
    """グローバル関数の使用方法"""

    def setUp(self):
        """テスト前のクリーンアップ"""
        reset_config_manager()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        reset_config_manager()

    def test_singleton_pattern_usage(self):
        """
        シングルトンパターンの使用

        get_config_manager()はアプリケーション全体で共有される単一のインスタンスを返します。
        """
        reset_config_manager()  # クリーンアップ

        # 同じインスタンスが返されることを確認
        cm1 = get_config_manager()
        cm2 = get_config_manager()
        assert cm1 is cm2

        # カスタムパスでの初期化（最初の呼び出しでのみ有効）
        reset_config_manager()

        sample_config = {"schema": {"root_path": "singleton_test"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm_custom = get_config_manager(f.name)
                assert cm_custom.get("schema.root_path") == "singleton_test"

                # 同じインスタンスが返される
                cm_same = get_config_manager()
                assert cm_custom is cm_same

            finally:
                os.unlink(f.name)
                reset_config_manager()

    def test_config_from_dictionary(self):
        """
        辞書からの設定マネージャー作成

        load_config_from_dict()はファイルを使わずに辞書から直接ConfigManagerを作成します。
        テストや動的設定生成に有用です。
        """
        config_dict = {
            "schema": {"root_path": "dict_schema", "cache_enabled": False},
            "validation": {"strict_mode": True, "max_errors_per_object": 75},
            "output": {"format": "detailed_json", "log_level": "DEBUG"},
        }

        cm = load_config_from_dict(config_dict)

        # 辞書の内容が正しく設定されていることを確認
        assert isinstance(cm, ConfigManager)
        assert cm.get("schema.root_path") == "dict_schema"
        assert cm.get("schema.cache_enabled") is False
        assert cm.get("validation.strict_mode") is True
        assert cm.get("validation.max_errors_per_object") == 75
        assert cm.get("output.format") == "detailed_json"
        assert cm.get("output.log_level") == "DEBUG"

        # 型付きメソッドも正常に動作する
        schema_root = cm.get_schema_root_path()
        assert schema_root.is_absolute()  # 絶対パスを返すことを確認
        assert schema_root.name == "dict_schema"  # ディレクトリ名が正しいことを確認
        assert cm.get_cache_enabled() is False
        assert cm.is_strict_mode() is True
        assert cm.get_log_level() == "DEBUG"

        # 空の辞書からも作成可能
        cm_empty = load_config_from_dict({})
        assert isinstance(cm_empty, ConfigManager)
        assert cm_empty.get("nonexistent.key", "default") == "default"


class TestConfigManagerStringRepresentation:
    """文字列表現の説明"""

    def test_string_representations(self):
        """
        ConfigManagerの文字列表現

        __str__()と__repr__()メソッドはデバッグやログ出力に有用です。
        """
        sample_config = {
            "schema": {"root_path": "test_schema"},
            "output": {"log_level": "INFO"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)

                # __str__() - ユーザー向けの表現
                str_repr = str(cm)
                assert isinstance(str_repr, str)
                assert "ConfigManager" in str_repr
                assert "test_schema" in str_repr

                # __repr__() - デバッグ向けの表現
                repr_str = repr(cm)
                assert isinstance(repr_str, str)
                assert "ConfigManager" in repr_str
                assert "config_path" in repr_str

                print(f"String representation: {str_repr}")
                print(f"Debug representation: {repr_str}")

            finally:
                os.unlink(f.name)


class TestConfigManagerAdvancedUsage:
    """高度な使用方法の説明"""

    def test_full_configuration_export(self):
        """
        全設定の取得とエクスポート

        get_config_dict()は現在の設定を辞書として取得します。
        """
        sample_config = {
            "schema": {"root_path": "export_test", "cache_enabled": True},
            "validation": {"strict_mode": False, "max_errors_per_object": 100},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)

                # 設定を変更
                cm.set("output.format", "json")
                cm.set("testing.enabled", True)

                # 全設定の取得
                config_dict = cm.get_config_dict()

                assert isinstance(config_dict, dict)
                assert "schema" in config_dict
                assert "validation" in config_dict
                assert "output" in config_dict  # 新しく追加された
                assert "testing" in config_dict  # 新しく追加された

                assert config_dict["schema"]["root_path"] == "export_test"
                assert config_dict["validation"]["strict_mode"] is False
                assert config_dict["output"]["format"] == "json"
                assert config_dict["testing"]["enabled"] is True

            finally:
                os.unlink(f.name)

    def test_real_world_usage_example(self):
        """
        実際の使用例のシミュレーション

        JSON Validatorでの典型的な使用パターンを示します。
        """
        # アプリケーション起動時の設定読み込み
        app_config = {
            "schema": {
                "root_path": "schema",
                "cache_enabled": True,
                "custom_paths": [],
            },
            "validation": {
                "strict_mode": True,
                "max_errors_per_object": 100,
                "allow_additional_properties": False,
            },
            "output": {"format": "json", "include_warnings": True, "log_level": "INFO"},
            "testing": {"samples_dir": "samples", "test_data_dir": "test_data"},
        }

        # 環境変数による設定上書き（本番環境での設定調整）
        with patch.dict(
            "os.environ",
            {
                "VALIDATOR_SCHEMA_ROOT_PATH": "/production/schemas",
                "VALIDATOR_OUTPUT_LOG_LEVEL": "WARNING",
                "VALIDATOR_VALIDATION_STRICT_MODE": "false",
            },
        ):
            cm = load_config_from_dict(app_config)

            # バリデーターが使用する設定値の取得
            schema_root = cm.get_schema_root_path()
            is_strict = cm.is_strict_mode()
            max_errors = cm.get("validation.max_errors_per_object")
            log_level = cm.get_log_level()
            samples_dir = cm.get_samples_dir()

            # 環境変数による上書きが反映されていることを確認
            assert str(schema_root) == "/production/schemas"  # 環境変数で上書き
            assert is_strict is False  # 環境変数で上書き
            assert log_level == "WARNING"  # 環境変数で上書き
            assert max_errors == 100  # 元の設定値
            # 絶対パスが返されることを確認
            assert samples_dir.is_absolute()
            assert samples_dir.name == "samples"  # ディレクトリ名が正しいことを確認

            # 設定の検証
            validation_errors = cm.validate_config()
            assert len(validation_errors) == 0  # 設定に問題なし

            print(f"Schema root: {schema_root}")
            print(f"Strict mode: {is_strict}")
            print(f"Max errors: {max_errors}")
            print(f"Log level: {log_level}")
            print(f"Samples directory: {samples_dir}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
