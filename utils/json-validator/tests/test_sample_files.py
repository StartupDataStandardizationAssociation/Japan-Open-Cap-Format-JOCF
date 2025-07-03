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
from unittest.mock import patch
from parameterized import parameterized

# テスト対象のクラス
from validator.main import JSONValidator
from validator.schema_loader import SchemaLoader
from validator.validation_result import ValidationResult
from validator.config import get_config



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
        self.validator = JSONValidator()
        
        # サンプルディレクトリが存在するかチェック
        self.assertTrue(self.samples_dir.exists(), 
                       f"サンプルディレクトリが存在しません: {self.samples_dir}")
        
        # スキーマローダーの初期化
        try:
            self.validator.schema_loader.load_all_schemas()
        except Exception as e:
            # スキーマローダーでエラーが発生した場合はログに記録
            print(f"Warning: スキーマの読み込みでエラーが発生しました: {e}")
    
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
        self.assertIsInstance(result, ValidationResult)
        self.assertIsInstance(result.is_valid, bool)
        self.assertIsInstance(result.errors, list)
        
        # エラーがある場合の詳細チェック
        if not result.is_valid:
            print(f"\n{filename} validation errors:")
            for error in result.errors:
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
            
            if result.is_valid:
                valid_files += 1
            else:
                invalid_files += 1
                print(f"\nCase file {case_file.name} errors:")
                for error in result.errors:
                    print(f"  - {error}")
        
        print(f"\nCase files summary: {valid_files} valid, {invalid_files} invalid")
        
        # すべてのケースファイルでバリデーションエラーが発生していないことを確認
        self.assertEqual(invalid_files, 0, f"ケースファイルでバリデーションエラーが発生しています: {invalid_files}個のファイルでエラー")
        self.assertEqual(valid_files, len(case_files), "すべてのケースファイルが有効である必要があります")
    
    def test_validate_j_kiss_files(self):
        """j-kiss_2ディレクトリ内のファイルをテスト"""
        j_kiss_dir = self.samples_dir / "j-kiss_2"
        
        if not j_kiss_dir.exists():
            self.skipTest("j-kiss_2 directory not found")
        
        j_kiss_files = []
        for numbered_dir in j_kiss_dir.iterdir():
            if numbered_dir.is_dir():
                for jocf_file in numbered_dir.glob("*.jocf.json"):
                    j_kiss_files.append(jocf_file)
        
        self.assertGreater(len(j_kiss_files), 0, "J-KISSファイルが見つかりませんでした")
        
        valid_files = 0
        invalid_files = 0
        
        for j_kiss_file in j_kiss_files:
            result = self.validator.validate(str(j_kiss_file))
            
            if result.is_valid:
                valid_files += 1
            else:
                invalid_files += 1
                print(f"\nJ-KISS file {j_kiss_file.name} errors:")
                for error in result.errors:
                    print(f"  - {error}")
        
        print(f"\nJ-KISS files summary: {valid_files} valid, {invalid_files} invalid")
        
        # すべてのJ-KISSファイルでバリデーションエラーが発生していないことを確認
        self.assertEqual(invalid_files, 0, f"J-KISSファイルでバリデーションエラーが発生しています: {invalid_files}個のファイルでエラー")
        self.assertEqual(valid_files, len(j_kiss_files), "すべてのJ-KISSファイルが有効である必要があります")
    
    def test_validate_seeds_files(self):
        """seedsディレクトリ内のファイルをテスト"""
        seeds_dir = self.samples_dir / "seeds"
        
        if not seeds_dir.exists():
            self.skipTest("seeds directory not found")
        
        seeds_files = list(seeds_dir.glob("*.jocf.json"))
        
        self.assertGreater(len(seeds_files), 0, "Seedsファイルが見つかりませんでした")
        
        valid_files = 0
        invalid_files = 0
        
        for seeds_file in seeds_files:
            result = self.validator.validate(str(seeds_file))
            
            if result.is_valid:
                valid_files += 1
            else:
                invalid_files += 1
                print(f"\nSeeds file {seeds_file.name} errors:")
                for error in result.errors:
                    print(f"  - {error}")
        
        print(f"\nSeeds files summary: {valid_files} valid, {invalid_files} invalid")
        
        # ネットワークエラー（外部スキーマアクセス）が発生していないことを確認
        all_errors = []
        for seeds_file in seeds_files:
            result = self.validator.validate(str(seeds_file))
            all_errors.extend(result.errors)
        network_errors = [error for error in all_errors if 'HTTPSConnectionPool' in error or 'Failed to resolve' in error]
        self.assertEqual(len(network_errors), 0, "ネットワークエラーが発生しています - スキーマの$ref解決に問題があります")
        
        # すべてのSEEDSファイルでバリデーションエラーが発生していないことを確認
        self.assertEqual(invalid_files, 0, f"SEEDSファイルでバリデーションエラーが発生しています: {invalid_files}個のファイルでエラー")
        self.assertEqual(valid_files, len(seeds_files), "すべてのSEEDSファイルが有効である必要があります")
    
    def test_validate_stock_repurchase_files(self):
        """stock_repurchaseディレクトリ内のファイルをテスト"""
        stock_repurchase_dir = self.samples_dir / "stock_repurchase"
        
        if not stock_repurchase_dir.exists():
            self.skipTest("stock_repurchase directory not found")
        
        stock_repurchase_files = list(stock_repurchase_dir.glob("*.jocf.json"))
        
        self.assertGreater(len(stock_repurchase_files), 0, "Stock repurchaseファイルが見つかりませんでした")
        
        valid_files = 0
        invalid_files = 0
        
        for repurchase_file in stock_repurchase_files:
            result = self.validator.validate(str(repurchase_file))
            
            if result.is_valid:
                valid_files += 1
            else:
                invalid_files += 1
                print(f"\nStock repurchase file {repurchase_file.name} errors:")
                for error in result.errors:
                    print(f"  - {error}")
        
        print(f"\nStock repurchase files summary: {valid_files} valid, {invalid_files} invalid")
        
        # すべてのStock repurchaseファイルでバリデーションエラーが発生していないことを確認
        self.assertEqual(invalid_files, 0, f"Stock repurchaseファイルでバリデーションエラーが発生しています: {invalid_files}個のファイルでエラー")
        self.assertEqual(valid_files, len(stock_repurchase_files), "すべてのStock repurchaseファイルが有効である必要があります")
    
    def test_validate_stocktransfer_files(self):
        """stocktransferディレクトリ内のファイルをテスト"""
        stocktransfer_dir = self.samples_dir / "stocktransfer"
        
        if not stocktransfer_dir.exists():
            self.skipTest("stocktransfer directory not found")
        
        stocktransfer_files = list(stocktransfer_dir.glob("*.jocf.json"))
        
        self.assertGreater(len(stocktransfer_files), 0, "Stock transferファイルが見つかりませんでした")
        
        valid_files = 0
        invalid_files = 0
        
        for transfer_file in stocktransfer_files:
            result = self.validator.validate(str(transfer_file))
            
            if result.is_valid:
                valid_files += 1
            else:
                invalid_files += 1
                print(f"\nStock transfer file {transfer_file.name} errors:")
                for error in result.errors:
                    print(f"  - {error}")
        
        print(f"\nStock transfer files summary: {valid_files} valid, {invalid_files} invalid")
        
        # すべてのStock transferファイルでバリデーションエラーが発生していないことを確認
        self.assertEqual(invalid_files, 0, f"Stock transferファイルでバリデーションエラーが発生しています: {invalid_files}個のファイルでエラー")
        self.assertEqual(valid_files, len(stocktransfer_files), "すべてのStock transferファイルが有効である必要があります")
    
    def test_validate_all_sample_directories(self):
        """すべてのサンプルディレクトリを網羅的にテスト"""
        sample_directories = [
            ("cases", "ケース"),
            ("j-kiss_2", "J-KISS"),
            ("seeds", "シード"),
            ("stock_repurchase", "株式買い戻し"),
            ("stocktransfer", "株式譲渡")
        ]
        
        total_files = 0
        total_valid = 0
        total_invalid = 0
        
        print(f"\n{'='*60}")
        print("全サンプルディレクトリの検証結果:")
        print(f"{'='*60}")
        
        for dir_name, display_name in sample_directories:
            sample_dir = self.samples_dir / dir_name
            
            if not sample_dir.exists():
                print(f"{display_name}ディレクトリ ({dir_name}) が存在しません - スキップ")
                continue
            
            # ディレクトリ内のJOCFファイルを検索
            if dir_name in ["cases", "j-kiss_2"]:
                # サブディレクトリ構造を持つディレクトリ
                files = []
                for subdir in sample_dir.iterdir():
                    if subdir.is_dir():
                        for numbered_dir in subdir.iterdir():
                            if numbered_dir.is_dir():
                                files.extend(numbered_dir.glob("*.jocf.json"))
                            else:
                                files.extend([numbered_dir] if numbered_dir.suffix == ".json" and "jocf" in numbered_dir.name else [])
            else:
                # 直接JOCFファイルを持つディレクトリ
                files = list(sample_dir.glob("*.jocf.json"))
            
            if not files:
                print(f"{display_name}: ファイルが見つかりませんでした")
                continue
                
            valid_files = 0
            invalid_files = 0
            
            for file_path in files:
                result = self.validator.validate(str(file_path))
                if result.is_valid:
                    valid_files += 1
                else:
                    invalid_files += 1
            
            total_files += len(files)
            total_valid += valid_files
            total_invalid += invalid_files
            
            print(f"{display_name}: {len(files)}ファイル (有効: {valid_files}, 無効: {invalid_files})")
        
        print(f"{'='*60}")
        print(f"合計: {total_files}ファイル (有効: {total_valid}, 無効: {total_invalid})")
        print(f"成功率: {(total_valid/total_files*100):.1f}%" if total_files > 0 else "成功率: N/A")
        print(f"{'='*60}")
        
        # すべてのサンプルファイルでバリデーションエラーが発生していないことを確認
        self.assertGreater(total_files, 0, "サンプルファイルが1つも見つかりませんでした")
        self.assertEqual(total_invalid, 0, f"サンプルファイルでバリデーションエラーが発生しています: {total_invalid}個のファイルでエラー")
        self.assertEqual(total_valid, total_files, "すべてのサンプルファイルが有効である必要があります")
    
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