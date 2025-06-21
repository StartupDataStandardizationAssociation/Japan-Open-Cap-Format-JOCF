# ADR-0001: RefResolver遅延初期化の採用

## ステータス

承認済み (2025-06-21)

## コンテキスト

SchemaLoaderクラスにおいて、JSONSchema参照解決のためのRefResolverをいつ初期化するかについて設計決定が必要でした。以下の選択肢が考慮されました：

1. **即座初期化**: `__init__()`メソッド内でRefResolverを構築
2. **eager初期化**: `load_all_schemas()`メソッド完了時にRefResolverを構築  
3. **遅延初期化**: `get_ref_resolver()`が初回呼び出された時にRefResolverを構築

## 決定

**遅延初期化（Lazy Initialization）**を採用する。

```python
def get_ref_resolver(self) -> RefResolver:
    if self.ref_resolver is None:
        self.ref_resolver = self._build_ref_resolver()
    return self.ref_resolver
```

## 理由

### 1. 依存関係の適切な解決

RefResolverは全てのスキーマ（file_type_map, object_type_map）がロードされた後に構築する必要があります：

- `__init__()`時点では、スキーママップは空
- `load_all_schemas()`後に、初めて完全なスキーマセットが利用可能
- 遅延初期化により、常に最新の完全なスキーマセットでRefResolverを構築

### 2. パフォーマンス最適化

RefResolver構築は重い処理（100+スキーマの処理）であり、不要な場合は回避すべき：

```python
# RefResolverを使わない軽量操作
loader.get_file_schema("JOCF_TRANSACTIONS_FILE")  # RefResolver不要

# RefResolverが必要な時のみ構築
resolver = loader.get_ref_resolver()  # ここで初めて構築
```

### 3. 動的スキーマ変更への対応

実行時にスキーマが追加/変更される場合に対応：

```python
loader.load_all_schemas()
# 後からスキーマを動的追加
loader.file_type_map["CUSTOM_TYPE"] = custom_schema
# get_ref_resolver()が呼ばれた時に最新状態で構築される
```

### 4. テスタビリティの向上

部分的なテストが可能：

```python
# スキーマロードのみのテスト
loader.load_all_schemas()
assert len(loader.file_type_map) == 4

# RefResolver機能のテスト（必要時のみ）
resolver = loader.get_ref_resolver()
assert resolver.resolution_scope == expected_base_uri
```

## 代替案と却下理由

### 代替案1: 即座初期化（`__init__()`内）

```python
def __init__(self, config_manager: ConfigManager):
    # ...
    self.ref_resolver = self._build_ref_resolver()  # ❌ 空のマップで構築
```

**却下理由**: スキーマが未ロードの状態でRefResolverを構築することになり、無意味

### 代替案2: eager初期化（`load_all_schemas()`完了時）

```python
def load_all_schemas(self) -> None:
    self.load_file_schemas()
    self.load_object_schemas()
    self.ref_resolver = self._build_ref_resolver()  # 常に構築
```

**却下理由**: 
- RefResolverを使わない場合も常に重い処理が実行される
- 動的なスキーマ変更に対応しにくい
- 単一責任の原則に反する（load_all_schemas()がRefResolver構築も担当）

## 影響

### 正の影響
- 必要な時のみRefResolver構築 → パフォーマンス向上
- 動的スキーマ変更に対応 → 柔軟性向上  
- 依存関係が明確 → 保守性向上
- テストの分離が可能 → テスタビリティ向上

### 負の影響
- 初回`get_ref_resolver()`呼び出し時に遅延発生（軽微）
- 実装がわずかに複雑（None チェックが必要）

## 実装詳細

```python
class SchemaLoader:
    def __init__(self, config_manager: ConfigManager):
        # ...
        self.ref_resolver = None  # 初期状態はNone
    
    def get_ref_resolver(self) -> RefResolver:
        if self.ref_resolver is None:
            self.ref_resolver = self._build_ref_resolver()
        return self.ref_resolver
    
    def _build_ref_resolver(self) -> RefResolver:
        # 全スキーマを含むstoreを構築
        store = {}
        for schema in self.file_type_map.values():
            if schema_id := schema.get("$id"):
                store[schema_id] = schema
        # ...
        return RefResolver(base_uri, None, store=store)
```

## 検証方法

1. **機能テスト**: RefResolverが正しく$ref解決することを確認
2. **パフォーマンステスト**: RefResolver未使用時の軽量性を確認
3. **統合テスト**: 実際のJOCFファイルでの動作確認

## メモ

- この決定は TDD (Test-Driven Development) アプローチで実装され、15個のテストケースで検証済み
- jsonschema.RefResolverは非推奨だが、互換性のために継続使用
- 将来的には referencing ライブラリへの移行を検討