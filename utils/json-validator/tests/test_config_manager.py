#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigManagerクラスと関連グローバル関数のTDDテスト

テスト対象：
- ConfigManagerクラスの全メソッドの期待される挙動
- 正常系、境界値テスト、異常系のテスト
- グローバル関数（get_config_manager, reset_config_manager, load_config_from_dict）のテスト
- 環境変数による設定上書き機能

注意：
現在のConfigManagerクラスは未実装状態です。このテストは期待される挙動に基づいて作成されており、
実装完了時に実際に動作することを前提としています（TDDアプローチ）。
"""

import pytest
import json
import tempfile
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, mock_open

# テスト対象のクラスと関数
from validator.config_manager import (
    ConfigManager,
    get_config_manager,
    reset_config_manager,
    load_config_from_dict,
    _global_config_manager,
)
from validator.exceptions import ConfigError


class TestConfigManagerInit:
    """ConfigManager.__init__()のテスト"""

    def test_init_without_config_path_uses_default(self):
        """デフォルト設定パスでの初期化"""
        cm = ConfigManager()

        # デフォルトパスが設定されること
        assert cm.get_config_file_path().name == "validator_config.json"

    def test_init_with_custom_config_path(self):
        """カスタム設定パスでの初期化"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_config = {
                "schema": {"root_path": "custom_schema"},
                "validation": {"strict_mode": False},
            }
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                assert cm.get_config_file_path() == Path(f.name)
            finally:
                os.unlink(f.name)

    def test_init_with_nonexistent_path_raises_error(self):
        """存在しないパスでの初期化時エラー"""
        with pytest.raises(ConfigError) as exc_info:
            ConfigManager("/nonexistent/path/config.json")

        assert "Config file not found" in str(exc_info.value)

    def test_init_with_invalid_json_raises_error(self):
        """無効なJSONファイルでの初期化時エラー"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            f.flush()

            try:
                with pytest.raises(ConfigError) as exc_info:
                    ConfigManager(f.name)

                assert "Invalid JSON format" in str(exc_info.value)
            finally:
                os.unlink(f.name)

    def test_init_with_permission_error(self):
        """権限エラーでの初期化時エラー"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "config"}, f)
            f.flush()

            try:
                # ファイルの読み取り権限を削除
                os.chmod(f.name, 0o000)

                with pytest.raises(ConfigError) as exc_info:
                    ConfigManager(f.name)

                assert "Permission denied" in str(exc_info.value)
            finally:
                os.chmod(f.name, 0o644)  # 権限を復元してから削除
                os.unlink(f.name)


class TestConfigManagerLoadConfig:
    """ConfigManager.load_config()のテスト"""

    def test_load_valid_json_config(self):
        """有効なJSONファイルの読み込み"""
        test_config = {
            "schema": {"root_path": "test_schema", "cache_enabled": True},
            "validation": {"strict_mode": False, "max_errors_per_object": 50},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()

                assert cm.get("schema.root_path") == "test_schema"
                assert cm.get("schema.cache_enabled") is True
                assert cm.get("validation.strict_mode") is False
                assert cm.get("validation.max_errors_per_object") == 50
            finally:
                os.unlink(f.name)

    def test_load_config_file_not_found(self):
        """存在しないファイルの読み込みエラー"""
        cm = ConfigManager.__new__(ConfigManager)
        cm._config_path = Path("/nonexistent/config.json")

        with pytest.raises(ConfigError) as exc_info:
            cm.load_config()

        assert "Config file not found" in str(exc_info.value)

    def test_load_config_invalid_json(self):
        """無効なJSONの読み込みエラー"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            f.flush()

            try:
                cm = ConfigManager.__new__(ConfigManager)
                cm._config_path = Path(f.name)

                with pytest.raises(ConfigError) as exc_info:
                    cm.load_config()

                assert "Invalid JSON format" in str(exc_info.value)
            finally:
                os.unlink(f.name)

    def test_load_config_permission_denied(self):
        """権限エラーでの読み込みエラー"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "config"}, f)
            f.flush()

            try:
                os.chmod(f.name, 0o000)

                cm = ConfigManager.__new__(ConfigManager)
                cm._config_path = Path(f.name)

                with pytest.raises(ConfigError) as exc_info:
                    cm.load_config()

                assert "Permission denied" in str(exc_info.value)
            finally:
                os.chmod(f.name, 0o644)
                os.unlink(f.name)


class TestConfigManagerGet:
    """ConfigManager.get()のテスト"""

    @pytest.fixture
    def sample_config_manager(self):
        """サンプル設定でConfigManagerを作成"""
        test_config = {
            "schema": {
                "root_path": "test_schema",
                "cache_enabled": True,
                "nested": {"deep": {"value": "deep_value"}},
            },
            "validation": {"strict_mode": False, "max_errors_per_object": 100},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()
                return cm
            finally:
                os.unlink(f.name)

    def test_get_existing_key(self, sample_config_manager):
        """既存キーの取得"""
        cm = sample_config_manager

        assert cm.get("schema.root_path") == "test_schema"
        assert cm.get("schema.cache_enabled") is True
        assert cm.get("validation.strict_mode") is False
        assert cm.get("validation.max_errors_per_object") == 100

    def test_get_nested_key_with_dot_notation(self, sample_config_manager):
        """ドット記法でのネストキー取得"""
        cm = sample_config_manager

        assert cm.get("schema.nested.deep.value") == "deep_value"

    def test_get_with_default_value(self, sample_config_manager):
        """デフォルト値の使用"""
        cm = sample_config_manager

        # 存在しないキーにデフォルト値
        assert cm.get("nonexistent.key", "default_value") == "default_value"
        assert cm.get("schema.nonexistent", 42) == 42
        assert cm.get("nonexistent", None) is None

    def test_get_empty_string_key(self, sample_config_manager):
        """空文字キーの処理"""
        cm = sample_config_manager

        with pytest.raises(ConfigError) as exc_info:
            cm.get("")

        assert "Invalid key path" in str(exc_info.value)

    def test_get_very_deep_nested_key(self, sample_config_manager):
        """非常に深いネストキーの取得"""
        cm = sample_config_manager

        # 存在しない深いネスト
        assert cm.get("schema.nested.deep.very.deep.key", "not_found") == "not_found"

    def test_get_nonexistent_key_without_default(self, sample_config_manager):
        """存在しないキー（デフォルト値なし）"""
        cm = sample_config_manager

        assert cm.get("nonexistent.key") is None


class TestConfigManagerSet:
    """ConfigManager.set()のテスト"""

    @pytest.fixture
    def sample_config_manager(self):
        """サンプル設定でConfigManagerを作成"""
        test_config = {
            "schema": {"root_path": "test_schema"},
            "validation": {"strict_mode": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()
                return cm
            finally:
                os.unlink(f.name)

    def test_set_existing_key(self, sample_config_manager):
        """既存キーの更新"""
        cm = sample_config_manager

        cm.set("schema.root_path", "new_schema_path")
        assert cm.get("schema.root_path") == "new_schema_path"

        cm.set("validation.strict_mode", False)
        assert cm.get("validation.strict_mode") is False

    def test_set_new_key(self, sample_config_manager):
        """新しいキーの設定"""
        cm = sample_config_manager

        cm.set("new.section.key", "new_value")
        assert cm.get("new.section.key") == "new_value"

        cm.set("schema.new_option", 42)
        assert cm.get("schema.new_option") == 42

    def test_set_nested_key(self, sample_config_manager):
        """ネストキーの設定"""
        cm = sample_config_manager

        cm.set("output.format.detailed.enabled", True)
        assert cm.get("output.format.detailed.enabled") is True

    def test_set_invalid_key_path(self, sample_config_manager):
        """無効なキーパスでのエラー"""
        cm = sample_config_manager

        with pytest.raises(ConfigError) as exc_info:
            cm.set("", "value")

        assert "Invalid key path" in str(exc_info.value)

        with pytest.raises(ConfigError) as exc_info:
            cm.set("key..double.dot", "value")

        assert "Invalid key path" in str(exc_info.value)


class TestConfigManagerSpecificGetters:
    """設定取得メソッド群のテスト"""

    @pytest.fixture
    def full_config_manager(self):
        """完全な設定でConfigManagerを作成"""
        test_config = {
            "schema": {
                "root_path": "test_schema",
                "cache_enabled": True,
                "custom_paths": ["/path1", "/path2"],
            },
            "validation": {
                "strict_mode": True,
                "max_errors_per_object": 50,
                "allow_additional_properties": False,
            },
            "output": {
                "format": "detailed_json",
                "include_warnings": True,
                "log_level": "INFO",
            },
            "testing": {"samples_dir": "test_samples", "test_data_dir": "test_data"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()
                return cm
            finally:
                os.unlink(f.name)

    def test_get_schema_config(self, full_config_manager):
        """get_schema_config()の期待される戻り値"""
        cm = full_config_manager
        schema_config = cm.get_schema_config()

        assert isinstance(schema_config, dict)
        assert schema_config["root_path"] == "test_schema"
        assert schema_config["cache_enabled"] is True
        assert schema_config["custom_paths"] == ["/path1", "/path2"]

    def test_get_validation_config(self, full_config_manager):
        """get_validation_config()の期待される戻り値"""
        cm = full_config_manager
        validation_config = cm.get_validation_config()

        assert isinstance(validation_config, dict)
        assert validation_config["strict_mode"] is True
        assert validation_config["max_errors_per_object"] == 50
        assert validation_config["allow_additional_properties"] is False

    def test_get_output_config(self, full_config_manager):
        """get_output_config()の期待される戻り値"""
        cm = full_config_manager
        output_config = cm.get_output_config()

        assert isinstance(output_config, dict)
        assert output_config["format"] == "detailed_json"
        assert output_config["include_warnings"] is True
        assert output_config["log_level"] == "INFO"

    def test_get_testing_config(self, full_config_manager):
        """get_testing_config()の期待される戻り値"""
        cm = full_config_manager
        testing_config = cm.get_testing_config()

        assert isinstance(testing_config, dict)
        assert testing_config["samples_dir"] == "test_samples"
        assert testing_config["test_data_dir"] == "test_data"


class TestConfigManagerBooleanMethods:
    """ブール型メソッドのテスト"""

    @pytest.fixture
    def boolean_config_manager(self):
        """ブール設定のConfigManagerを作成"""
        test_config = {
            "schema": {"cache_enabled": True},
            "validation": {"strict_mode": False},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()
                return cm
            finally:
                os.unlink(f.name)

    def test_get_cache_enabled(self, boolean_config_manager):
        """get_cache_enabled()のブール値テスト"""
        cm = boolean_config_manager

        cache_enabled = cm.get_cache_enabled()
        assert isinstance(cache_enabled, bool)
        assert cache_enabled is True

    def test_is_strict_mode(self, boolean_config_manager):
        """is_strict_mode()のブール値テスト"""
        cm = boolean_config_manager

        strict_mode = cm.is_strict_mode()
        assert isinstance(strict_mode, bool)
        assert strict_mode is False

    def test_boolean_methods_with_missing_config(self):
        """ブール設定が欠如している場合のデフォルト値"""
        test_config = {"schema": {"root_path": "test"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()

                # デフォルト値が返されることを確認
                assert isinstance(cm.get_cache_enabled(), bool)
                assert isinstance(cm.is_strict_mode(), bool)
            finally:
                os.unlink(f.name)


class TestConfigManagerPathMethods:
    """Path型メソッドのテスト"""

    @pytest.fixture
    def path_config_manager(self):
        """パス設定のConfigManagerを作成"""
        test_config = {
            "schema": {"root_path": "test_schema"},
            "testing": {"samples_dir": "test_samples"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()
                return cm
            finally:
                os.unlink(f.name)

    def test_get_schema_root_path(self, path_config_manager):
        """get_schema_root_path()のPath型検証"""
        cm = path_config_manager

        schema_path = cm.get_schema_root_path()
        assert isinstance(schema_path, Path)
        assert schema_path.is_absolute()  # 絶対パスを返すことを確認
        assert schema_path.name == "test_schema"  # ディレクトリ名が正しいことを確認

    def test_get_samples_dir(self, path_config_manager):
        """get_samples_dir()のPath型検証"""
        cm = path_config_manager

        samples_dir = cm.get_samples_dir()
        assert isinstance(samples_dir, Path)
        assert samples_dir.is_absolute()  # 絶対パスを返すことを確認
        assert samples_dir.name == "test_samples"  # ディレクトリ名が正しいことを確認

    def test_get_custom_schema_paths(self, path_config_manager):
        """get_custom_schema_paths()のList[Path]型検証"""
        cm = path_config_manager

        # カスタムパスを設定
        cm.set("schema.custom_paths", ["/path1", "/path2", "/path3"])

        custom_paths = cm.get_custom_schema_paths()
        assert isinstance(custom_paths, list)
        assert len(custom_paths) == 3
        assert all(isinstance(p, Path) for p in custom_paths)
        assert str(custom_paths[0]) == "/path1"
        assert str(custom_paths[1]) == "/path2"
        assert str(custom_paths[2]) == "/path3"


class TestConfigManagerEnvironmentVariables:
    """環境変数関連のテスト"""

    def test_environment_variable_override(self):
        """環境変数による設定上書き"""
        test_config = {
            "schema": {"root_path": "default_schema"},
            "validation": {"strict_mode": False},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                with patch.dict(
                    "os.environ",
                    {
                        "VALIDATOR_SCHEMA_ROOT_PATH": "/override/schema",
                        "VALIDATOR_VALIDATION_STRICT_MODE": "true",
                    },
                ):
                    cm = ConfigManager(f.name)
                    cm.load_config()

                    # 環境変数による上書きが適用されることを確認
                    assert cm.get("schema.root_path") == "/override/schema"
                    assert cm.get("validation.strict_mode") is True
            finally:
                os.unlink(f.name)

    def test_get_environment_overrides(self):
        """get_environment_overrides()の環境変数取得"""
        with patch.dict(
            "os.environ",
            {
                "VALIDATOR_SCHEMA_ROOT_PATH": "/env/schema",
                "VALIDATOR_TIMEOUT_SECONDS": "60",
                "OTHER_VARIABLE": "ignored",
            },
        ):
            cm = ConfigManager()
            env_overrides = cm.get_environment_overrides()

            assert isinstance(env_overrides, dict)
            assert "VALIDATOR_SCHEMA_ROOT_PATH" in env_overrides
            assert env_overrides["VALIDATOR_SCHEMA_ROOT_PATH"] == "/env/schema"
            assert "VALIDATOR_TIMEOUT_SECONDS" in env_overrides
            assert env_overrides["VALIDATOR_TIMEOUT_SECONDS"] == "60"
            assert "OTHER_VARIABLE" not in env_overrides

    def test_resolve_environment_variables(self):
        """_resolve_environment_variables()の環境変数解決"""
        with patch.dict("os.environ", {"TEST_VAR": "test_value"}):
            cm = ConfigManager()

            # 環境変数プレースホルダーの解決
            resolved = cm._resolve_environment_variables("${TEST_VAR}")
            assert resolved == "test_value"

            # 複数環境変数の解決
            resolved = cm._resolve_environment_variables("prefix_${TEST_VAR}_suffix")
            assert resolved == "prefix_test_value_suffix"

            # 存在しない環境変数の場合は元の値
            resolved = cm._resolve_environment_variables("${NONEXISTENT_VAR}")
            assert resolved == "${NONEXISTENT_VAR}"


class TestConfigManagerValidation:
    """設定検証関連のテスト"""

    def test_validate_config_valid(self):
        """有効な設定の検証"""
        test_config = {
            "schema": {"root_path": "valid_schema", "cache_enabled": True},
            "validation": {"strict_mode": True, "max_errors_per_object": 100},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()

                validation_errors = cm.validate_config()
                assert isinstance(validation_errors, list)
                assert len(validation_errors) == 0  # エラーなし
            finally:
                os.unlink(f.name)

    def test_validate_config_invalid(self):
        """無効な設定の検証"""
        test_config = {
            "schema": {"root_path": None},  # 無効な値
            "validation": {"max_errors_per_object": -1},  # 負の値
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()

                validation_errors = cm.validate_config()
                assert isinstance(validation_errors, list)
                assert len(validation_errors) > 0  # エラーが存在

                # エラーメッセージの検証
                error_messages = " ".join(validation_errors)
                assert "root_path" in error_messages
                assert "max_errors_per_object" in error_messages
            finally:
                os.unlink(f.name)


class TestConfigManagerStringMethods:
    """文字列メソッドのテスト"""

    @pytest.fixture
    def string_config_manager(self):
        """文字列設定のConfigManagerを作成"""
        test_config = {
            "output": {"log_level": "DEBUG"},
            "schema": {"root_path": "test_schema"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()
                return cm
            finally:
                os.unlink(f.name)

    def test_get_log_level(self, string_config_manager):
        """get_log_level()の文字列型テスト"""
        cm = string_config_manager

        log_level = cm.get_log_level()
        assert isinstance(log_level, str)
        assert log_level == "DEBUG"

    def test_str_method(self, string_config_manager):
        """__str__()メソッドのテスト"""
        cm = string_config_manager

        str_repr = str(cm)
        assert isinstance(str_repr, str)
        assert "ConfigManager" in str_repr
        assert "test_schema" in str_repr or "log_level" in str_repr

    def test_repr_method(self, string_config_manager):
        """__repr__()メソッドのテスト"""
        cm = string_config_manager

        repr_str = repr(cm)
        assert isinstance(repr_str, str)
        assert "ConfigManager" in repr_str
        assert "config_path" in repr_str or "Config" in repr_str


class TestGlobalFunctions:
    """グローバル関数のテスト"""

    def setup_method(self):
        """各テストメソッド実行前の初期化"""
        reset_config_manager()

    def teardown_method(self):
        """各テストメソッド実行後のクリーンアップ"""
        reset_config_manager()

    def test_get_config_manager_singleton(self):
        """get_config_manager()のシングルトン動作"""
        cm1 = get_config_manager()
        cm2 = get_config_manager()

        # 同じインスタンスが返されることを確認
        assert cm1 is cm2

    def test_get_config_manager_with_custom_path(self):
        """get_config_manager()でのカスタムパス指定"""
        test_config = {"schema": {"root_path": "custom_schema"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = get_config_manager(f.name)
                assert cm.get_config_file_path() == Path(f.name)
                assert cm.get("schema.root_path") == "custom_schema"
            finally:
                os.unlink(f.name)

    def test_reset_config_manager(self):
        """reset_config_manager()のリセット機能"""
        cm1 = get_config_manager()
        reset_config_manager()
        cm2 = get_config_manager()

        # リセット後は新しいインスタンスが返されることを確認
        assert cm1 is not cm2

    def test_load_config_from_dict(self):
        """load_config_from_dict()の辞書からの設定読み込み"""
        test_config = {
            "schema": {"root_path": "dict_schema", "cache_enabled": False},
            "validation": {"strict_mode": True, "max_errors_per_object": 75},
        }

        cm = load_config_from_dict(test_config)

        assert isinstance(cm, ConfigManager)
        assert cm.get("schema.root_path") == "dict_schema"
        assert cm.get("schema.cache_enabled") is False
        assert cm.get("validation.strict_mode") is True
        assert cm.get("validation.max_errors_per_object") == 75

    def test_load_config_from_dict_empty(self):
        """load_config_from_dict()での空辞書処理"""
        cm = load_config_from_dict({})

        assert isinstance(cm, ConfigManager)
        # デフォルト値が適用されることを確認
        assert cm.get("nonexistent.key", "default") == "default"


class TestConfigManagerFileOperations:
    """ファイル操作関連のテスト"""

    @pytest.fixture
    def temp_config_dir(self):
        """一時設定ディレクトリの作成"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_save_config(self, temp_config_dir):
        """save_config()での設定保存"""
        test_config = {
            "schema": {"root_path": "save_test", "cache_enabled": True},
            "validation": {"strict_mode": False},
        }

        # 元の設定ファイル作成
        original_file = Path(temp_config_dir) / "original.json"
        with open(original_file, "w") as f:
            json.dump(test_config, f)

        cm = ConfigManager(str(original_file))
        cm.load_config()

        # 設定を変更
        cm.set("schema.root_path", "modified_schema")
        cm.set("validation.strict_mode", True)

        # 新しいファイルに保存
        output_file = Path(temp_config_dir) / "saved.json"
        cm.save_config(str(output_file))

        # 保存されたファイルを検証
        assert output_file.exists()
        with open(output_file, "r") as f:
            saved_config = json.load(f)

        assert saved_config["schema"]["root_path"] == "modified_schema"
        assert saved_config["validation"]["strict_mode"] is True

    def test_reload_config(self, temp_config_dir):
        """reload_config()での設定再読み込み"""
        test_config = {
            "schema": {"root_path": "original_schema"},
            "validation": {"strict_mode": True},
        }

        config_file = Path(temp_config_dir) / "reload_test.json"
        with open(config_file, "w") as f:
            json.dump(test_config, f)

        cm = ConfigManager(str(config_file))
        cm.load_config()

        assert cm.get("schema.root_path") == "original_schema"

        # ファイルを外部から変更
        modified_config = {
            "schema": {"root_path": "modified_schema"},
            "validation": {"strict_mode": False},
        }
        with open(config_file, "w") as f:
            json.dump(modified_config, f)

        # 設定を再読み込み
        cm.reload_config()

        assert cm.get("schema.root_path") == "modified_schema"
        assert cm.get("validation.strict_mode") is False

    def test_merge_config(self, temp_config_dir):
        """merge_config()での設定マージ"""
        base_config = {
            "schema": {"root_path": "base_schema", "cache_enabled": True},
            "validation": {"strict_mode": True},
        }

        config_file = Path(temp_config_dir) / "merge_test.json"
        with open(config_file, "w") as f:
            json.dump(base_config, f)

        cm = ConfigManager(str(config_file))
        cm.load_config()

        # マージする設定
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

    def test_reset_to_defaults(self, temp_config_dir):
        """reset_to_defaults()でのデフォルト値リセット"""
        test_config = {
            "schema": {"root_path": "custom_schema"},
            "validation": {"strict_mode": False},
        }

        config_file = Path(temp_config_dir) / "reset_test.json"
        with open(config_file, "w") as f:
            json.dump(test_config, f)

        cm = ConfigManager(str(config_file))
        cm.load_config()

        # カスタム設定を確認
        assert cm.get("schema.root_path") == "custom_schema"
        assert cm.get("validation.strict_mode") is False

        # デフォルトにリセット
        cm.reset_to_defaults()

        # デフォルト値が適用されていることを確認
        # （具体的なデフォルト値は実装に依存）
        schema_config = cm.get_schema_config()
        validation_config = cm.get_validation_config()

        assert isinstance(schema_config, dict)
        assert isinstance(validation_config, dict)
        assert "root_path" in schema_config
        assert "strict_mode" in validation_config


class TestConfigManagerAdvanced:
    """高度な機能のテスト"""

    def test_get_config_dict(self):
        """get_config_dict()での全設定取得"""
        test_config = {
            "schema": {"root_path": "test_schema", "cache_enabled": True},
            "validation": {"strict_mode": False, "max_errors_per_object": 100},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            f.flush()

            try:
                cm = ConfigManager(f.name)
                cm.load_config()

                config_dict = cm.get_config_dict()

                assert isinstance(config_dict, dict)
                assert "schema" in config_dict
                assert "validation" in config_dict
                assert config_dict["schema"]["root_path"] == "test_schema"
                assert config_dict["schema"]["cache_enabled"] is True
                assert config_dict["validation"]["strict_mode"] is False
                assert config_dict["validation"]["max_errors_per_object"] == 100
            finally:
                os.unlink(f.name)

    def test_nested_value_operations(self):
        """_get_nested_value()と_set_nested_value()の内部メソッドテスト"""
        cm = ConfigManager()

        # テスト用の設定辞書
        test_dict = {"level1": {"level2": {"level3": "deep_value"}}}

        # ネスト値の取得テスト
        value = cm._get_nested_value(test_dict, "level1.level2.level3")
        assert value == "deep_value"

        # 存在しないキーの場合
        value = cm._get_nested_value(test_dict, "nonexistent.key")
        assert value is None

        # ネスト値の設定テスト
        cm._set_nested_value(test_dict, "level1.level2.new_key", "new_value")
        assert test_dict["level1"]["level2"]["new_key"] == "new_value"

        # 新しいネスト構造の作成
        cm._set_nested_value(test_dict, "new.nested.structure", "created")
        assert test_dict["new"]["nested"]["structure"] == "created"


if __name__ == "__main__":
    pytest.main([__file__])
