# RefResolver から Registry への移行実装

## 概要
JSONスキーマライブラリのRefResolverが非推奨になったため、新しいRegistry APIへの完全移行を実施しました。

## 背景
- `jsonschema`ライブラリのRefResolverがv4.18.0で非推奨化
- 新しい`referencing`ライブラリのRegistry APIへの移行が必要
- 大量の非推奨警告とテスト失敗の解消が急務

## 作業内容

### 1. 依存関係の更新
**ファイル**: `requirements.txt`
```diff
+ referencing>=0.35.0
```

### 2. SchemaLoaderの移行
**ファイル**: `utils/json-validator/validator/schema_loader.py`

**主要変更**:
- `RefResolver` → `Registry`への完全移行
- `get_ref_resolver()` → `get_registry()`メソッド名変更
- `_build_ref_resolver()` → `_build_registry()`実装更新

**具体的な実装**:
```python
# Before
from jsonschema import RefResolver
self.ref_resolver: Optional[RefResolver] = None

def get_ref_resolver(self) -> RefResolver:
    if self.ref_resolver is None:
        self.ref_resolver = self._build_ref_resolver()
    return self.ref_resolver

# After  
from referencing import Registry
from referencing.jsonschema import DRAFT202012
self.registry: Optional[Registry] = None

def get_registry(self) -> Registry:
    if self.registry is None:
        self.registry = self._build_registry()
    return self.registry

def _build_registry(self) -> Registry:
    registry = Registry()
    for schema in self.file_type_map.values():
        schema_id = schema.get("$id")
        if schema_id:
            resource = DRAFT202012.create_resource(schema)
            registry = registry.with_resource(schema_id, resource)
    # オブジェクトスキーマも同様に追加
    return registry
```

### 3. ObjectValidatorの移行
**ファイル**: `utils/json-validator/validator/object_validator.py`

**主要変更**:
- 例外処理の更新: `jsonschema.RefResolutionError` → `referencing.exceptions.Unresolvable`
- 検証パラメータの変更: `resolver=` → `registry=`

### 4. テストファイルの全面更新

#### test_object_validator.py
**修正対象**: 3つの失敗していたテストメソッド
- `test_validate_object_with_ref_resolution`
- `test_validate_object_nested_ref_resolution_error` 
- `test_validate_with_jsonschema_success`

**修正内容**:
```python
# Before
from jsonschema import RefResolver
resolver = RefResolver("https://...", schema, store=store)
mock_schema_loader.get_ref_resolver.return_value = resolver
mock_validate.assert_called_once_with(data, schema, resolver=resolver)

# After
from referencing import Registry
from referencing.jsonschema import DRAFT202012
registry = Registry()
resource = DRAFT202012.create_resource(schema)
registry = registry.with_resource(schema_id, resource)
mock_schema_loader.get_registry.return_value = registry
mock_validate.assert_called_once_with(data, schema, registry=registry)
```

#### test_main.py
**問題**: Mock registryがiteration可能でないエラー
**解決策**: 実際のRegistryインスタンスを使用
```python
# Before (Mock使用 - エラー)
mock_resolver = Mock()
mock_schema_loader.get_registry.return_value = mock_resolver

# After (実際のRegistry使用)
from referencing import Registry
from referencing.jsonschema import DRAFT202012
registry = Registry()
test_schema = {...}
resource = DRAFT202012.create_resource(test_schema)
registry = registry.with_resource("https://test.example.com/test-schema.json", resource)
mock_schema_loader.get_registry.return_value = registry
```

#### test_schema_loader_specs.py
**主要更新**:
- `TestSchemaLoaderRegistryIntegrationSpecs`クラスの改善
- 意味のない存在確認テストから実際の統合テストへ変更

**Before**: 
```python
def test_registry_store_completeness_spec(self):
    registry = self.loader.get_registry()
    self.assertIsInstance(registry, Registry)  # 意味のないテスト

def test_ref_resolution_functionality_spec(self):
    registry = self.loader.get_registry()  
    self.assertIsInstance(registry, Registry)  # 意味のないテスト
```

**After**:
```python
def test_registry_integration_with_jsonschema_validation(self):
    # 実際のjsonschema.validate()でRegistry統合をテスト
    registry = self.loader.get_registry()
    schema = self.loader.get_object_schema(ObjectType('TX_STOCK_ISSUANCE'))
    test_data = {...}  # 有効なテストデータ
    jsonschema.validate(test_data, schema, registry=registry)
    # $ref解決を含む実際の検証をテスト
```

### 5. その他のファイル更新
- `test_object_validator_specs.py`: Mockオブジェクトの更新
- `test_schema_loader.py`: 存在確認（該当箇所なし）

## 結果

### テスト成功率
- **Before**: 286/303 tests passing (94.4%) + RefResolver非推奨警告
- **After**: 302/303 tests passing (99.7%) → **303/303 tests passing (100%)**

### 非推奨警告
- **Before**: 大量のRefResolver非推奨警告
- **After**: **完全に除去**

### API変更サマリー
| 項目 | Before | After |
|------|---------|-------|
| ライブラリ | `jsonschema.RefResolver` | `referencing.Registry` |
| メソッド | `get_ref_resolver()` | `get_registry()` |
| パラメータ | `resolver=` | `registry=` |
| 例外 | `RefResolutionError` | `Unresolvable` |
| 作成方法 | `RefResolver(base_uri, schema, store)` | `Registry().with_resource(id, resource)` |

## 技術的課題と解決策

### 1. Mock vs 実際のオブジェクト
**問題**: RegistryのMockオブジェクトがiteration可能でない
**解決**: 実際のRegistryインスタンスを使用（テストの実用性も向上）

### 2. スキーマデータ形式の違い
**問題**: テストデータの`currency_code`フィールドがスキーマの`currency`と不一致
**発見**: Registry統合テストにより実際のスキーマ検証エラーを検出
**解決**: 正しいフィールド名に修正

### 3. Registry API理解
**学習**: 
- Registry は直接的なstore accessを提供しない
- `DRAFT202012.create_resource()` でスキーマをResourceに変換
- `registry.with_resource(id, resource)` で immutable に追加

## 今後の保守性向上

### 1. テスト品質向上
- 意味のないMockテストから実用的な統合テストへ移行
- 実際のschema validation を通じた$ref解決テスト

### 2. API設計の一貫性
- 全てのコンポーネントでRegistry使用に統一
- 例外処理の統一（Unresolvable使用）

### 3. 将来の互換性
- `referencing`ライブラリのベストプラクティスに準拠
- jsonschemaライブラリの将来バージョンとの互換性確保

## まとめ
RefResolver廃止対応を完全に完了し、全テストを通過させることに成功しました。新しいRegistry APIにより、より安定した$ref解決機能を実現し、将来のjsonschemaライブラリアップデートにも対応可能な基盤を構築しました。