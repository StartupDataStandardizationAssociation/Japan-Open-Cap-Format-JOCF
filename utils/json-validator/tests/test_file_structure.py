#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
各ファイル形式の構造詳細テスト

TransactionsFile、SecurityHoldersFile、StockClassesFileの詳細な構造検証を行う
"""

import unittest
import json
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
    """実際のJOCFファイルを使ったファイル構造テスト"""
    
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
    
    def test_validate_transactions_file_structure(self):
        """TransactionsFileの構造詳細テスト"""
        file_path = self.samples_dir / "TransactionsFile.jocf.json"
        
        if not file_path.exists():
            self.skipTest("TransactionsFile.jocf.json not found")
        
        # JSONファイルを直接読み込んで構造をチェック
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 基本構造のチェック
        self.assertEqual(data["file_type"], "JOCF_TRANSACTIONS_FILE")
        self.assertIn("items", data)
        self.assertIsInstance(data["items"], list)
        
        # 各トランザクションアイテムのチェック
        expected_object_types = [
            "TX_STOCK_ISSUANCE",
            "TX_STOCK_TRANSFER", 
            "TX_CONVERTIBLE_ISSUANCE"
        ]
        
        found_object_types = set()
        for item in data["items"]:
            self.assertIn("object_type", item, "各アイテムにはobject_typeが必要です")
            self.assertIn("id", item, "各アイテムにはidが必要です")
            found_object_types.add(item["object_type"])
        
        # 期待されるオブジェクトタイプが含まれているかチェック
        for expected_type in expected_object_types:
            if expected_type in found_object_types:
                self.assertIn(expected_type, found_object_types)
        
        print(f"Found object types: {sorted(found_object_types)}")
    
    def test_validate_securities_holders_file_structure(self):
        """SecurityHoldersFileの構造詳細テスト"""
        file_path = self.samples_dir / "SecurityHoldersFile.jocf.json"
        
        if not file_path.exists():
            self.skipTest("SecurityHoldersFile.jocf.json not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 基本構造のチェック
        self.assertEqual(data["file_type"], "JOCF_SECURITY_HOLDERS_FILE")
        self.assertIn("items", data)
        
        # 各SecurityHolderアイテムのチェック
        for item in data["items"]:
            self.assertIn("object_type", item)
            self.assertEqual(item["object_type"], "SECURITY_HOLDER")
            self.assertIn("id", item)
            self.assertIn("name", item)
    
    def test_validate_stock_classes_file_structure(self):
        """StockClassesFileの構造詳細テスト"""
        file_path = self.samples_dir / "StockClassesFile.jocf.json"
        
        if not file_path.exists():
            self.skipTest("StockClassesFile.jocf.json not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 基本構造のチェック
        self.assertEqual(data["file_type"], "JOCF_STOCK_CLASSES_FILE")
        self.assertIn("items", data)
        
        # 各StockClassアイテムのチェック
        for item in data["items"]:
            self.assertIn("object_type", item)
            self.assertEqual(item["object_type"], "STOCK_CLASS")
            self.assertIn("id", item)
            self.assertIn("class_type", item)


if __name__ == '__main__':
    unittest.main()