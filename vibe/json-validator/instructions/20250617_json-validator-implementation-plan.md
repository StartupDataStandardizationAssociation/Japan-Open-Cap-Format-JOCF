# JSONバリデーター実装計画（TDD方式）

既存の単体テスト（[`utils/json-validator/tests/`](utils/json-validator/tests/)）を活用したテスト駆動開発（TDD）方式でJSONバリデーターを実装します。この計画は[`tmp/test-analysis-report.md`](tmp/test-analysis-report.md) の分析結果に基づき、Red-Green-Refactorサイクルに従った段階的な実装アプローチを採用します。

## 1. TDD実装アプローチ

### 1.1 TDDサイクルと実装順序
```mermaid
graph TD
    A[🔴 Red<br/>テスト実行・失敗確認] --> B[🟢 Green<br/>最小限実装・テスト成功]
    B --> C[🔵 Refactor<br/>コード改善・品質向上]
    C --> D[次のフェーズ]
    
    E[ValidationResult] --> F[SchemaLoader]
    F --> G[ObjectValidator]
    G --> H[FileValidator] 
    H --> I[JSONValidator統合]
    
    style A fill:#ffebee
    style B fill:#e8f5e8
    style C fill:#e3f2fd
```

### 1.2 実装の基本方針
- **テストファースト**: 仕様を明確化してから実装
- **段階的構築**: 依存関係に基づく順序で各コンポーネントを実装
- **継続的品質**: 各段階でのテスト成功とリファクタリング

## 2. ファイル構成とクラス設計

```
utils/json-validator/
├── validate.sh                    # メインエントリーポイント
├── validator/
│   ├── __init__.py
│   ├── main.py                     # 統合処理
│   ├── validation_result.py        # 検証結果クラス
│   ├── schema_loader.py            # スキーマ管理
│   ├── file_validator.py           # ファイル検証
│   ├── object_validator.py         # オブジェクト検証
│   └── exceptions.py               # 例外処理
└── tests/                          # 既存テストファイル
    ├── test_schema_loader.py
    ├── test_file_validator.py
    ├── test_object_validator.py
    └── test_integration.py
```

### 2.1 主要クラスの責務分離
- **ValidationResult**: 検証結果の管理と構造化
- **SchemaLoader**: スキーマファイルの読み込みとインデックス作成
- **ObjectValidator**: 個別オブジェクトの検証処理
- **FileValidator**: JOCFファイル構造の検証
- **JSONValidator**: 統合処理とエンドツーエンド検証

## 3. TDD実装フェーズ詳細

### Phase 1: ValidationResult基盤構築（半日）

#### 🔴 Red: テスト失敗確認
```bash
python -m pytest utils/json-validator/tests/ -k "ValidationResult" -v
```

#### 🟢 Green: 最小限実装
```python
class ValidationResult:
    def __init__(self, is_valid: bool = True, errors: list = None, 
                 file_path: str = None, validated_objects: int = 0):
        self.is_valid = is_valid
        self.errors = errors or []
        self.file_path = file_path
        self.validated_objects = validated_objects
    
    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.is_valid = False
    
    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "file_path": self.file_path,
            "validated_objects": self.validated_objects
        }
```

#### 🔵 Refactor: 品質向上
- エラーメッセージの構造化
- 型ヒントの完全化
- ドキュメンテーション

### Phase 2: SchemaLoader実装（1.5日）

#### 🔴 Red: 段階的テスト実行
```bash
python -m pytest utils/json-validator/tests/test_schema_loader.py::test_load_all_schemas_success -v
python -m pytest utils/json-validator/tests/test_schema_loader.py::test_get_file_schema_success -v
python -m pytest utils/json-validator/tests/test_schema_loader.py::test_ref_resolver_setup -v
```

#### 🟢 Green: 段階的実装
```python
class SchemaLoader:
    def __init__(self):
        self.file_type_map = {}
        self.object_type_map = {}
        self.ref_resolver = None
        self.schema_root_path = Path("schema")
    
    def load_all_schemas(self) -> None:
        # schema/files/*.schema.json の読み込み
        # schema/objects/*.schema.json の読み込み
        # インデックス作成
    
    def get_file_schema(self, file_type: str) -> dict | None:
        return self.file_type_map.get(file_type)
    
    def get_object_schema(self, object_type: str) -> dict | None:
        return self.object_type_map.get(object_type)
    
    def get_ref_resolver(self) -> RefResolver:
        # $ref解決のためのRefResolver構築
```

#### 🔵 Refactor: 最適化
- スキーマキャッシュ機構
- パフォーマンス最適化（大量スキーマ処理対応）
- エラーハンドリング強化

### Phase 3: ObjectValidator実装（1日）

#### 🔴 Red: 基本機能テスト
```bash
python -m pytest utils/json-validator/tests/test_object_validator.py::test_validate_object_success_stock_issuance -v
python -m pytest utils/json-validator/tests/test_object_validator.py::test_validate_object_with_ref_resolution -v
```

#### 🟢 Green: 検証機能実装
```python
class ObjectValidator:
    def __init__(self, schema_loader: SchemaLoader):
        self.schema_loader = schema_loader
    
    def validate_object(self, object_data: dict) -> ValidationResult:
        # object_type取得
        # 対応スキーマ取得
        # jsonschema.validate()実行
        # ValidationResult作成
```

#### 🔵 Refactor: エラー詳細化
- 具体的なエラーメッセージ
- ネストした$ref解決対応
- 検証パスの追跡

### Phase 4: FileValidator実装（1日）

#### 🔴 Red: ファイル構造テスト
```bash
python -m pytest utils/json-validator/tests/test_file_validator.py::test_validate_file_success -v
python -m pytest utils/json-validator/tests/test_file_validator.py::test_validate_items_array_success -v
```

#### 🟢 Green: ファイル検証実装
```python
class FileValidator:
    def __init__(self, schema_loader: SchemaLoader):
        self.schema_loader = schema_loader
        self.object_validator = ObjectValidator(schema_loader)
    
    def validate_file(self, file_data: dict) -> ValidationResult:
        # file_type検証
        # 必須属性チェック
        # items配列の各要素をObjectValidatorで検証
```

#### 🔵 Refactor: 大量データ対応
- 検証順序の最適化
- メモリ効率の改善
- エラー収集の効率化

### Phase 5: JSONValidator統合（1日）

#### 🔴 Red: 統合テスト実行
```bash
python -m pytest utils/json-validator/tests/test_integration.py::test_validate_success_with_valid_file -v
python -m pytest utils/json-validator/tests/test_integration.py -v
```

#### 🟢 Green: 統合クラス実装
```python
class JSONValidator:
    def __init__(self):
        self.schema_loader = SchemaLoader()
        self.file_validator = FileValidator(self.schema_loader)
    
    def validate(self, file_path: str) -> ValidationResult:
        # ファイル読み込み
        # FileValidatorによる検証
        # 結果の統合と返却
```

#### 🔵 Refactor: 最終最適化
- エラーハンドリングの統一
- ログ出力の整備
- パフォーマンス調整

## 4. 既存テストケースの活用戦略

### 4.1 テストケース分析結果
```mermaid
mindmap
  root((既存テストケース))
    SchemaLoader
      正常系: 全スキーマ読み込み、インデックス作成
      異常系: 存在しないスキーマ、JSONパースエラー
      境界値: 大量スキーマ処理（100個）
    FileValidator
      正常系: 有効ファイル検証、items配列検証
      異常系: file_type不正、必須項目不足
      境界値: 大量items配列（1000個）
    ObjectValidator
      正常系: 各種オブジェクト検証、$ref解決
      異常系: object_type不正、スキーマ検証エラー
    統合テスト
      正常系: エンドツーエンド検証
      異常系: ファイル不存在、無効JSON
```

### 4.2 TDD実装のメリット
- **品質保証**: テストによる仕様の明確化と回帰テスト
- **開発効率**: 早期バグ発見と安全なリファクタリング
- **保守性向上**: テストコードが仕様書の役割

## 5. 技術的考慮事項

### 5.1 パフォーマンス要件（テストから導出）
```python
# 大量スキーマ処理: 100個のスキーマファイル処理が2秒以内
# 大量オブジェクト検証: 1000個のオブジェクト検証が5秒以内
```

### 5.2 エラーハンドリング戦略
- **段階的エラー処理**: 各レイヤーでの適切なエラーハンドリング
- **具体的エラーメッセージ**: ユーザーが問題を特定しやすい情報提供
- **構造化エラー出力**: JSON形式での詳細なエラー情報

## 6. 使用方法と最終成果物

### 6.1 基本的な使用方法
```bash
# JOCFファイルの検証
./utils/json-validator/validate.sh samples/TransactionsFile.jocf.json

# 品質指標（TDDにより保証）
✅ 全テストケース成功率: 100%
✅ コードカバレッジ: 90%以上
✅ 型チェック: エラーなし
✅ パフォーマンス: 要求水準クリア
```

### 6.2 出力形式

#### 成功時
```json
{
  "status": "success",
  "message": "検証が成功しました",
  "file_path": "samples/TransactionsFile.jocf.json",
  "validated_objects": 5,
  "validation_time": "0.123s"
}
```

#### 失敗時
```json
{
  "status": "error",
  "message": "ファイル検証に失敗しました",
  "details": {
    "file_path": "samples/TransactionsFile.jocf.json",
    "errors": [
      {
        "field": "file_type",
        "message": "file_type属性が存在しません",
        "expected": "string",
        "actual": "undefined"
      }
    ]
  }
}
```

## 7. 継続的品質改善

### 7.1 CI/CDパイプライン
```bash
# 自動テスト実行
python -m pytest utils/json-validator/tests/ -v --cov=validator --cov-report=html
```

### 7.2 将来的な拡張対応
- **新しいfile_type対応**: 既存テスト構造の拡張
- **新しいobject_type対応**: テストケースの追加
- **パフォーマンス要件変更**: 境界値テストの調整

### 7.3 TDD実装による実現価値
- **🔒 堅牢性**: 全機能がテストで保証済み
- **🚀 開発速度**: 安全なリファクタリングが可能
- **📚 仕様明確化**: テストコードが実装仕様を文書化
- **🔄 保守性**: 変更影響範囲の明確化

このTDD実装計画により、既存のテストケースを最大限活用し、品質と開発効率を両立した堅牢なJSONバリデーターを段階的に構築できます。Red-Green-Refactorサイクルを通じて、確実に動作する実装を保証します。