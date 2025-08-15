# JSON Validator

JOCFファイルの検証を行うPythonバリデーターです。

## 概要

Japan Open Cap Format (JOCF) のJSONファイルを検証するためのツールです。階層化されたJSONスキーマ（files, objects, types, primitives, enums）に基づいて、ファイル全体および個別オブジェクトの検証を行います。

## 主要コンポーネント

- **SchemaLoader**: スキーマファイルの読み込み、インデックス作成、$ref解決
- **FileValidator**: トップレベルJOCFファイルの検証
- **ObjectValidator**: 個別オブジェクトの検証  
- **ConfigManager**: 設定ファイルの管理

## 使用方法

```python
from validator.schema_loader import SchemaLoader
from validator.config_manager import ConfigManager

# 設定とスキーマローダーの初期化
config = ConfigManager()
loader = SchemaLoader(config)
loader.load_all_schemas()

# ファイルスキーマの取得
transactions_schema = loader.get_file_schema('JOCF_TRANSACTIONS_FILE')

# $ref解決
resolver = loader.get_ref_resolver()
```

## テスト実行

```bash
# 全テスト実行
python -m pytest tests/

# スキーマローダーのテスト
python -m pytest tests/test_schema_loader.py -v

# カバレッジ付きテスト
python -m pytest tests/ --cov=validator
```

## 設定

設定は `config/validator_config.json` で管理されます：

## 依存関係

- Python3.13
- 詳細は requirements.txt を参照
