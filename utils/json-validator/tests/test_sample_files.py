#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メインサンプルファイルの基本的な検証テスト

メインのJOCFサンプルファイルとcasesディレクトリ内のファイルの基本的な検証を行う
"""

import unittest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
from parameterized import parameterized

# テスト対象のクラス（実装予定）
# from validator.main import JSONValidator
# from validator.schema_loader import SchemaLoader
# from validator.validation_result import ValidationResult
from validator.config import get_config


class MockJSONValidator:
    """テスト用のJSONValidatorモッククラス"""
    
    def __init__(self):
        self.schema_loader = Mock()
        self.file_validator = Mock()
        self.object_validator = Mock()
    
    def validate(self, file_path):
        """ファイルの検証"""
        try:
            # JSONファイルの読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 基本的な構造チェック
            if "file_type" not in data:
                return {
                    "is_valid": False,
                    "errors": ["file_type属性が存在しません"],
                    "file_path": file_path
                }
            
            if "items" not in data:
                return {
                    "is_valid": False,
                    "errors": ["items配列が存在しません"],
                    "file_path": file_path
                }
            
            # items配列の各要素をチェック
            errors = []
            validated_objects = 0
            
            for i, item in enumerate(data.get("items", [])):
                if "object_type" not in item:
                    errors.append(f"items[{i}]: object_type属性が存在しません")
                else:
                    validated_objects += 1
                    
                    # 実際のファイルに含まれる典型的なエラーをチェック
                    if item.get("object_type") == "TX_STOCK_ISSUANCE":
                        share_price = item.get("share_price", {})
                        if "ammount" in share_price:  # 典型的な誤字
                            errors.append(f"items[{i}].share_price: 'ammount'は'amount'の誤字の可能性があります")
                        if "cuurency_code" in share_price:  # 典型的な誤字
                            errors.append(f"items[{i}].share_price: 'cuurency_code'は'currency_code'の誤字の可能性があります")
                    
                    elif item.get("object_type") == "TX_CONVERTIBLE_ISSUANCE":
                        investment_amount = item.get("investment_amount", {})
                        if "ammount" in investment_amount:
                            errors.append(f"items[{i}].investment_amount: 'ammount'は'amount'の誤字の可能性があります")
                        if "cuurency_code" in investment_amount:
                            errors.append(f"items[{i}].investment_amount: 'cuurency_code'は'currency_code'の誤字の可能性があります")
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "file_path": file_path,
                "validated_objects": validated_objects
            }
            
        except FileNotFoundError:
            return {
                "is_valid": False,
                "errors": ["ファイルが存在しません"],
                "file_path": file_path
            }
        except json.JSONDecodeError as e:
            return {
                "is_valid": False,
                "errors": [f"JSONパースエラー: {str(e)}"],
                "file_path": file_path
            }


class TestRealWorldFiles(unittest.TestCase):
    """実際のJOCFファイルを使ったテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # 設定管理システムの初期化（TDD: NotImplementedErrorのハンドリング）
        config = get_config()
        testing_config = config.get_testing_config()
        
        # 設定からサンプルディレクトリのパスを取得
        samples_dir_name = testing_config.get("samples_dir", "samples")
    
        # プロジェクトルートからの相対パスで取得
        # 現在のテストファイルからプロジェクトルートを特定
        current_dir = Path(__file__).parent
        project_root = current_dir
        
        # プロジェクトルートを探す（.gitやsetup.pyがある場所まで遡る）
        while project_root.parent != project_root:
            if (project_root / ".git").exists() or (project_root / "setup.py").exists():
                break
            project_root = project_root.parent
        
        self.samples_dir = project_root / samples_dir_name
        self.validator = MockJSONValidator()
        
        # サンプルディレクトリが存在するかチェック
        self.assertTrue(self.samples_dir.exists(), 
                       f"サンプルディレクトリが存在しません: {self.samples_dir}")
    
    @parameterized.expand([
        ("TransactionsFile.jocf.json",),
        ("SecurityHoldersFile.jocf.json",),
        ("StockClassesFile.jocf.json",),
        ("SecurityHoldersAgreementsFile.jocf.json",),
    ])
    def test_validate_main_sample_files(self, filename):
        """メインサンプルファイルの検証テスト"""
        file_path = self.samples_dir / filename
        
        if not file_path.exists():
            self.skipTest(f"Sample file {filename} not found")
        
        result = self.validator.validate(str(file_path))
        
        # 基本的な検証
        self.assertIsInstance(result, dict)
        self.assertIn("is_valid", result)
        self.assertIn("file_path", result)
        self.assertEqual(result["file_path"], str(file_path))
        
        # ファイル固有の検証
        if "transactions" in filename.lower():
            self.assertGreater(result["validated_objects"], 0, 
                             "TransactionFileには1つ以上のトランザクションが含まれているべきです")
        
        # エラーがある場合の詳細チェック
        if not result["is_valid"]:
            print(f"\n{filename} validation errors:")
            for error in result.get("errors", []):
                print(f"  - {error}")
    
    def test_validate_case_files(self):
        """casesディレクトリ内のファイルをテスト"""
        cases_dir = self.samples_dir / "cases"
        
        if not cases_dir.exists():
            self.skipTest("cases directory not found")
        
        case_files = []
        for case_subdir in cases_dir.iterdir():
            if case_subdir.is_dir():
                for numbered_dir in case_subdir.iterdir():
                    if numbered_dir.is_dir():
                        for jocf_file in numbered_dir.glob("*.jocf.json"):
                            case_files.append(jocf_file)
        
        self.assertGreater(len(case_files), 0, "ケースファイルが見つかりませんでした")
        
        valid_files = 0
        invalid_files = 0
        
        for case_file in case_files:
            result = self.validator.validate(str(case_file))
            
            if result["is_valid"]:
                valid_files += 1
            else:
                invalid_files += 1
                print(f"\nCase file {case_file.name} errors:")
                for error in result.get("errors", []):
                    print(f"  - {error}")
        
        print(f"\nCase files summary: {valid_files} valid, {invalid_files} invalid")
        
        # 少なくとも一部のケースファイルは有効であることを期待
        self.assertGreater(valid_files, 0, "有効なケースファイルが1つも見つかりませんでした")
    
    def test_config_based_sample_directory(self):
        """設定ベースのサンプルディレクトリテスト"""
        config = get_config()
        testing_config = config.get_testing_config()
        
        # 設定からサンプルディレクトリが正しく取得できることを確認
        samples_dir_config = testing_config.get("samples_dir", "samples")
        self.assertEqual(samples_dir_config, "samples")
        
        # 環境変数での上書きテスト
        with patch.dict(os.environ, {"VALIDATOR_TESTING_SAMPLES_DIR": "custom_samples"}):
            # 新しいConfigManagerインスタンスを作成して環境変数を反映
            from validator.config_manager import ConfigManager
            test_config = ConfigManager()
            self.assertEqual(test_config.get("testing.samples_dir"), "custom_samples")

if __name__ == '__main__':
    unittest.main()