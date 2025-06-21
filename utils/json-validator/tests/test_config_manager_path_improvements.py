#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigManagerのパスハンドリング改善機能のテスト

このテストファイルは、パスハンドリング改善によって追加された新機能をテストします。
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

from validator.config_manager import ConfigManager, load_config_from_dict
from validator.exceptions import ConfigError


class TestConfigManagerPathHandlingImprovements:
    """パスハンドリング改善機能のテスト"""

    def test_project_root_detection(self):
        """
        プロジェクトルート検出機能のテスト
        
        ConfigManagerは自動的にプロジェクトルートを検出し、
        相対パスの基準点として使用します。
        """
        cm = ConfigManager()
        project_root = cm.get_project_root()
        
        # プロジェクトルートが絶対パスであることを確認
        assert isinstance(project_root, Path)
        assert project_root.is_absolute()
        
        # プロジェクトルートが存在することを確認
        assert project_root.exists()
        assert project_root.is_dir()
        
        # プロジェクトルート内に期待されるファイル/ディレクトリが存在することを確認
        expected_items = ['schema', 'samples', 'utils']
        for item in expected_items:
            assert (project_root / item).exists(), f"{item} should exist in project root"

    def test_absolute_path_resolution(self):
        """
        絶対パス解決機能のテスト
        
        相対パスは自動的にプロジェクトルートからの絶対パスに変換されます。
        """
        sample_config = {
            "schema": {"root_path": "schema"},  # 相対パス
            "testing": {"samples_dir": "/absolute/samples"}  # 絶対パス
        }
        
        cm = load_config_from_dict(sample_config)
        project_root = cm.get_project_root()
        
        # 相対パスが絶対パスに変換されることを確認
        schema_path = cm.get_schema_root_path()
        assert schema_path.is_absolute()
        assert schema_path == project_root / "schema"
        
        # 絶対パスはそのまま使用されることを確認
        # （この場合は存在しないパスなので validate_exists=False）
        samples_path = cm.get_samples_dir(validate_exists=False)
        assert samples_path.is_absolute()
        assert str(samples_path) == "/absolute/samples"

    def test_path_validation_feature(self):
        """
        パス検証機能のテスト
        
        validate_exists=Trueを指定すると、パスの存在確認が行われます。
        """
        cm = ConfigManager()
        
        # 存在するパス（デフォルト設定）の検証
        try:
            schema_path = cm.get_schema_root_path(validate_exists=True)
            samples_path = cm.get_samples_dir(validate_exists=True)
            
            # 検証が成功した場合、パスが存在することを確認
            assert schema_path.exists()
            assert samples_path.exists()
        except ConfigError:
            # 存在しない場合は適切にエラーが発生することを確認
            pytest.fail("Default paths should exist in the project")
        
        # 存在しないパスの検証
        non_existent_config = {
            "schema": {"root_path": "non_existent_schema"},
            "testing": {"samples_dir": "non_existent_samples"}
        }
        
        cm_bad = load_config_from_dict(non_existent_config)
        
        # 存在しないパスで検証するとエラーが発生することを確認
        with pytest.raises(ConfigError) as exc_info:
            cm_bad.get_schema_root_path(validate_exists=True)
        assert "Schema root directory does not exist" in str(exc_info.value)
        assert "Project root:" in str(exc_info.value)
        
        with pytest.raises(ConfigError) as exc_info:
            cm_bad.get_samples_dir(validate_exists=True)
        assert "Samples directory does not exist" in str(exc_info.value)

    def test_validate_paths_method(self):
        """
        validate_paths()メソッドのテスト
        
        設定されたすべてのパスを一括で検証できます。
        """
        # 有効な設定
        cm = ConfigManager()
        path_errors = cm.validate_paths()
        
        # デフォルト設定では問題ないことを確認
        assert isinstance(path_errors, list)
        assert len(path_errors) == 0  # エラーなし
        
        # 無効な設定
        bad_config = {
            "schema": {"root_path": "non_existent_schema"},
            "testing": {"samples_dir": "non_existent_samples"}
        }
        
        cm_bad = load_config_from_dict(bad_config)
        path_errors = cm_bad.validate_paths()
        
        assert isinstance(path_errors, list)
        assert len(path_errors) > 0  # エラーが存在
        
        # エラーメッセージの内容確認
        error_text = " ".join(path_errors)
        assert "Schema root directory does not exist" in error_text
        assert "Samples directory does not exist" in error_text

    def test_working_directory_independence(self):
        """
        作業ディレクトリ非依存性のテスト
        
        異なる作業ディレクトリから実行しても、
        同じ絶対パスが返されることを確認します。
        """
        cm = ConfigManager()
        original_schema_path = cm.get_schema_root_path()
        
        # 一時ディレクトリに移動して実行
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # 異なる作業ディレクトリから新しいインスタンスを作成
                cm_new = ConfigManager()
                new_schema_path = cm_new.get_schema_root_path()
                
                # 同じ絶対パスが返されることを確認
                assert original_schema_path == new_schema_path
                assert original_schema_path.is_absolute()
                assert new_schema_path.is_absolute()
                
            finally:
                os.chdir(original_cwd)

    def test_mixed_absolute_and_relative_paths(self):
        """
        絶対パスと相対パスが混在する設定のテスト
        """
        mixed_config = {
            "schema": {
                "root_path": "schema",  # 相対パス
                "custom_paths": [
                    "/absolute/path1",          # 絶対パス
                    "relative/path2",           # 相対パス
                    "/absolute/path3",          # 絶対パス
                    "another/relative/path"     # 相対パス
                ]
            }
        }
        
        cm = load_config_from_dict(mixed_config)
        project_root = cm.get_project_root()
        
        # スキーマルートパス（相対パス）
        schema_path = cm.get_schema_root_path()
        assert schema_path.is_absolute()
        assert schema_path == project_root / "schema"
        
        # カスタムパス（混在）
        custom_paths = cm.get_custom_schema_paths()
        assert len(custom_paths) == 4
        
        # 絶対パスはそのまま
        assert str(custom_paths[0]) == "/absolute/path1"
        assert custom_paths[0].is_absolute()
        
        # 相対パスは絶対パスに変換
        assert custom_paths[1].is_absolute()
        assert custom_paths[1] == project_root / "relative/path2"
        
        # 絶対パスはそのまま
        assert str(custom_paths[2]) == "/absolute/path3"
        assert custom_paths[2].is_absolute()
        
        # 相対パスは絶対パスに変換
        assert custom_paths[3].is_absolute()
        assert custom_paths[3] == project_root / "another/relative/path"

    def test_error_messages_include_context(self):
        """
        エラーメッセージに十分なコンテキスト情報が含まれることを確認
        """
        bad_config = {
            "schema": {"root_path": "definitely_non_existent_directory"}
        }
        
        cm = load_config_from_dict(bad_config)
        
        try:
            cm.get_schema_root_path(validate_exists=True)
            pytest.fail("Should have raised ConfigError")
        except ConfigError as e:
            error_message = str(e)
            
            # エラーメッセージに含まれるべき情報
            assert "Schema root directory does not exist" in error_message
            assert "definitely_non_existent_directory" in error_message
            assert "Project root:" in error_message
            assert "Resolved from relative path" in error_message

    def test_backward_compatibility(self):
        """
        後方互換性のテスト
        
        既存のコードが動作し続けることを確認します。
        """
        cm = ConfigManager()
        
        # 既存のメソッドが引き続き動作することを確認
        schema_path = cm.get_schema_root_path()
        samples_dir = cm.get_samples_dir()
        custom_paths = cm.get_custom_schema_paths()
        
        # すべてPathオブジェクトであることを確認
        assert isinstance(schema_path, Path)
        assert isinstance(samples_dir, Path)
        assert isinstance(custom_paths, list)
        assert all(isinstance(p, Path) for p in custom_paths)
        
        # 新機能：すべて絶対パスであることを確認
        assert schema_path.is_absolute()
        assert samples_dir.is_absolute()
        assert all(p.is_absolute() for p in custom_paths)


class TestConfigManagerConfigFilePathImprovement:
    """設定ファイルパス指定の改善テスト"""

    def test_default_config_path_uses_project_root(self):
        """
        デフォルト設定ファイルパスがプロジェクトルートベースになることのテスト
        """
        cm = ConfigManager()
        config_path = cm.get_config_file_path()
        project_root = cm.get_project_root()
        
        # 設定ファイルパスが絶対パスであることを確認
        assert config_path.is_absolute()
        
        # 設定ファイルパスがプロジェクトルート配下にあることを確認
        assert str(config_path).startswith(str(project_root))
        
        # 期待される相対パス構造になっていることを確認
        expected_relative = "utils/json-validator/config/validator_config.json"
        assert config_path == project_root / expected_relative

    def test_relative_config_path_resolution(self):
        """
        相対設定ファイルパスがプロジェクトルートベースで解決されることのテスト
        """
        # 既存の設定ファイルを相対パスで指定
        relative_config_path = "utils/json-validator/config/validator_config.json"
        
        cm = ConfigManager(relative_config_path)
        config_path = cm.get_config_file_path()
        project_root = cm.get_project_root()
        
        # 絶対パスに変換されていることを確認
        assert config_path.is_absolute()
        
        # プロジェクトルートベースで解決されていることを確認
        assert config_path == project_root / relative_config_path


class TestConfigManagerProjectRootDetection:
    """プロジェクトルート検出の詳細テスト"""

    def test_marker_file_detection(self):
        """
        マーカーファイルによるプロジェクトルート検出のテスト
        """
        cm = ConfigManager()
        project_root = cm.get_project_root()
        
        # 期待されるマーカーファイルのいずれかが存在することを確認
        markers = ['.git', 'pyproject.toml', 'setup.py', 'requirements.txt', 'mkdocs.yml']
        marker_found = any((project_root / marker).exists() for marker in markers)
        
        assert marker_found, f"At least one marker file should exist in {project_root}"

    def test_fallback_behavior(self):
        """
        フォールバック動作のテスト
        
        マーカーファイルが見つからない場合でも、
        適切なフォールバックディレクトリが設定されることを確認します。
        """
        cm = ConfigManager()
        project_root = cm.get_project_root()
        
        # プロジェクトルートが有効なディレクトリであることを確認
        assert project_root.exists()
        assert project_root.is_dir()
        assert project_root.is_absolute()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])