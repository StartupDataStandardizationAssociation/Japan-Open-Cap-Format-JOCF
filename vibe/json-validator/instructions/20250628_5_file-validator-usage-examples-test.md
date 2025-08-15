# 20250628_5_file-validator-usage-examples-test.md

## 作業概要
FileValidatorの利用方法を示す単体テストの作成

## 背景・目的
- 既存の`test_file_validator.py`は包括的だが、利用方法が分かりにくい
- 開発者がFileValidatorを使い始める際の学習教材が必要
- 実際のJOCFファイルを使った実用的な使用例を提供
- TDDアプローチで段階的に学習できるテストケースの作成

## 実装内容

### 新規作成ファイル
- `utils/json-validator/tests/test_file_validator_usage_examples.py`

### TDDアプローチでの段階的実装

#### 🔴 Phase 1: 基本セットアップテスト
**実装内容:**
- ConfigManager、SchemaLoader、FileValidatorの基本的な初期化方法
- インスタンス生成の確認

**テストケース:**
- `test_basic_setup_and_initialization()`

**学習ポイント:**
```python
# Step 1: ConfigManagerを作成
config_manager = ConfigManager()

# Step 2: SchemaLoaderを初期化
schema_loader = SchemaLoader(config_manager)

# Step 3: スキーマをロード (重要!)
schema_loader.load_all_schemas()

# Step 4: FileValidatorを作成
file_validator = FileValidator(schema_loader)
```

#### 🟢 Phase 2: 正常系利用パターン
**実装内容:**
- 実際のサンプルファイル(`samples/TransactionsFile.jocf.json`)を使った検証
- ValidationResultの取得と確認方法

**テストケース:**
- `test_validate_real_jocf_file_basic_usage()`

**学習ポイント:**
- 実際のJOCFファイルの読み込み方法
- `validate_file()`メソッドの使用方法
- ValidationResultの基本的な活用方法

#### 🔵 Phase 3: 異常系パターンとエラーハンドリング
**実装内容:**
- よくあるエラーケースの検出方法
- エラーメッセージ分析の実用的なパターン

**テストケース:**
- `test_handle_common_validation_errors()`
- `test_error_message_analysis_pattern()`

**学習ポイント:**
- file_type不正の検出
- 必須フィールド不足の検出
- 無効なobject_typeの検出
- エラータイプの分類方法
- 詳細エラー情報の抽出方法

#### 🔄 Phase 4: 実用的な活用例
**実装内容:**
- 複数ファイルの一括検証パターン
- CI/CD向けの開発ワークフロー例

**テストケース:**
- `test_batch_file_validation_pattern()`
- `test_practical_development_workflow()`

**学習ポイント:**
- バッチ処理における進捗表示
- 検証結果のサマリー作成
- カスタムバリデーション関数の作成例
- CI/CD向けの結果判定パターン

## 実行結果

### テスト実行
```bash
$ python -m pytest utils/json-validator/tests/test_file_validator_usage_examples.py -v
```

**結果:** 6個のテストケース全て成功 ✅

### 発見された問題
実際のサンプルファイルで複数のエラーが検出され、FileValidatorが正常に動作していることを確認：

1. **object_typeのタイポ:** `TX_STOCK_OPTOIN_*` → `TX_STOCK_OPTION_*`
2. **必須フィールド不足:** `securityholder_id`, `date`などが欠如
3. **スキーマ不適合:** 実際のスキーマ定義と矛盾するフィールド

これらのエラーは、FileValidatorの厳密な検証機能が正常に動作していることを示している。

## 成果物の特徴

### 段階的学習設計
- **基本セットアップ** → **正常系** → **異常系** → **実用例** の順序で学習
- 各Phaseで必要な知識を段階的に習得可能

### 実用性重視
- 実際のJOCFファイルを使用
- 本番環境での利用パターンを想定
- CI/CDでの自動検証例を提供

### ドキュメンテーション機能
- テストケース自体が利用方法の説明となる
- コード例とコメントで使い方を明示
- 実際のエラーケースで学習効果を高める

### 実用的なヘルパー関数例
```python
def validate_jocf_file_with_detailed_logging(file_path: Path) -> dict:
    """
    詳細ログ付きでJOCFファイルを検証するヘルパー関数
    実際の開発で使用するカスタムバリデーション関数の例
    """
    # 検証時間、エラー分類、詳細レポート生成
    # CI/CD向けの結果判定ロジック
```

## 技術的な観点

### TDD原則の実践
- Red-Green-Refactorサイクルで開発
- 各Phaseで段階的に機能追加
- テストファーストアプローチによる品質確保

### コードの可読性
- 詳細なコメントとdocstring
- 実用的な変数名とメソッド名
- 段階的な説明構造

### 実用性の確保
- 実際の開発ワークフローを想定
- バッチ処理、エラーハンドリング、レポート生成
- 再利用可能なパターンの提供

## 今後の活用方法

### 開発者オンボーディング
新しい開発者がFileValidatorを学習する際の入門教材として活用

### ドキュメンテーション
公式ドキュメントの実装例として参照

### 継続的改善
実際の使用パターンに基づいた機能改善の指針として活用

## 結論
FileValidatorの利用方法を段階的に学習できる包括的なテストケース集を作成し、実用的な開発パターンを提供することができた。このテストファイルは、単なるテストケースを超えて、FileValidatorの実用的な活用ガイドとしての役割を果たす。