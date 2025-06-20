#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パフォーマンス関連のテスト

ファイル検証のパフォーマンス測定と並行処理のテストを行う
"""

import unittest
import json
import time
import concurrent.futures
from pathlib import Path
from unittest.mock import Mock

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
    """実際のJOCFファイルを使ったパフォーマンステスト"""
    
    def setUp(self):
        """テスト前の準備"""
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
    
    def test_performance_with_large_files(self):
        """大きなファイルでのパフォーマンステスト"""
        # 最大のファイルを見つける
        largest_file = None
        largest_size = 0
        
        for jocf_file in self.samples_dir.glob("**/*.jocf.json"):
            file_size = jocf_file.stat().st_size
            if file_size > largest_size:
                largest_size = file_size
                largest_file = jocf_file
        
        if largest_file is None:
            self.skipTest("No JOCF files found for performance testing")
        
        print(f"\nTesting performance with {largest_file.name} ({largest_size} bytes)")
        
        # パフォーマンス測定
        start_time = time.time()
        result = self.validator.validate(str(largest_file))
        elapsed_time = time.time() - start_time
        
        print(f"Validation completed in {elapsed_time:.3f} seconds")
        print(f"Objects validated: {result.get('validated_objects', 0)}")
        
        # パフォーマンス目標（仮）: 1秒以内で完了
        self.assertLess(elapsed_time, 1.0, 
                       f"バリデーションが遅すぎます: {elapsed_time:.3f}s")


class TestFileLoadingPerformance(unittest.TestCase):
    """ファイル読み込みパフォーマンステスト"""
    
    def setUp(self):
        config = get_config()
        testing_config = config.get_testing_config()
        samples_dir_name = testing_config.get("samples_dir", "samples")
        
        # プロジェクトルートからサンプルディレクトリを取得
        current_dir = Path(__file__).parent
        project_root = current_dir
        
        while project_root.parent != project_root:
            if (project_root / ".git").exists() or (project_root / "setup.py").exists():
                break
            project_root = project_root.parent
        
        self.samples_dir = project_root / samples_dir_name
        self.validator = MockJSONValidator()
    
    def test_concurrent_file_validation(self):
        """複数ファイルの並行検証テスト"""
        # テスト対象ファイルを収集
        jocf_files = list(self.samples_dir.glob("*.jocf.json"))
        
        if len(jocf_files) < 2:
            self.skipTest("Not enough JOCF files for concurrent testing")
        
        # 逐次処理の時間測定
        start_time = time.time()
        sequential_results = []
        for file_path in jocf_files:
            result = self.validator.validate(str(file_path))
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # 並行処理の時間測定
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            concurrent_results = list(executor.map(
                lambda f: self.validator.validate(str(f)), jocf_files
            ))
        concurrent_time = time.time() - start_time
        
        print(f"\nSequential validation: {sequential_time:.3f}s")
        print(f"Concurrent validation: {concurrent_time:.3f}s")
        print(f"Files processed: {len(jocf_files)}")
        
        # 結果の整合性チェック
        self.assertEqual(len(sequential_results), len(concurrent_results))
        
        # 並行処理が逐次処理よりも速いことを期待（ファイル数が多い場合）
        if len(jocf_files) >= 4:
            self.assertLess(concurrent_time, sequential_time * 0.8,
                           "並行処理による速度向上が見られません")


if __name__ == '__main__':
    unittest.main()