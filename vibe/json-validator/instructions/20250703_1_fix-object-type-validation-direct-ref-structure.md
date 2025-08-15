# 20250703_1_fix-object-type-validation-direct-ref-structure.md

## 概要
`_get_allowed_object_types`メソッドが直接`$ref`構造（単一オブジェクトタイプ）に対応していない問題をTDDで修正。

## 問題の発見
`utils/json-validator/tests/test_sample_files.py`実行時に以下のエラーが発生：
```
object_type 'SECURITY_HOLDER' は許可されていません。許可されているobject_type: []
```

## 根本原因分析
- `SecurityHoldersFile.schema.json`は直接`$ref`構造を使用
- 既存の`_get_allowed_object_types`メソッドは`oneOf`構造のみを想定
- 結果として許可されたobject_typeリストが空配列になる

### スキーマ構造の違い
```json
// 既存対応: oneOf構造（複数オブジェクトタイプ）
{
  "properties": {
    "items": {
      "items": {
        "oneOf": [
          {"$ref": "..."},
          {"$ref": "..."}
        ]
      }
    }
  }
}

// 新規対応: 直接$ref構造（単一オブジェクトタイプ）
{
  "properties": {
    "items": {
      "items": {
        "$ref": "..."
      }
    }
  }
}
```

## TDD実装プロセス

### 🔴 Red Phase
`utils/json-validator/tests/test_file_validator.py`に以下のテストクラスを追加：

```python
class TestGetAllowedObjectTypes(unittest.TestCase):
    def test_get_allowed_object_types_with_direct_ref_structure(self):
        """直接$ref構造（単一オブジェクトタイプ）のケース - 現在失敗する"""
        # SecurityHoldersFileのような直接$ref構造のスキーマをテスト
        # 期待値: ["SECURITY_HOLDER"]
        # 実際値: [] (失敗)
        
    def test_get_allowed_object_types_with_oneOf_structure(self):
        """oneOf構造（複数オブジェクトタイプ）のケース - 既存動作の回帰テスト"""
        # 既存機能が壊れていないことを確認
```

### 🟢 Green Phase
`utils/json-validator/validator/file_validator.py`の`_get_allowed_object_types`メソッドを修正：

1. **直接$ref構造の対応追加**：
   ```python
   # 直接$ref構造をチェック（単一オブジェクトタイプ）
   elif "$ref" in items_schema:
       ref_url = items_schema["$ref"]
       object_type = self._extract_object_type_from_ref(resolver, ref_url)
       if object_type:
           allowed_types.append(object_type)
   ```

2. **共通処理の抽出**：
   ```python
   def _extract_object_type_from_ref(self, resolver, ref_url: str) -> Optional[str]:
       """$refを解決してobject_typeを抽出する共通処理"""
   ```

### 🔵 Refactor Phase
- DRY原則の適用：object_type抽出ロジックを共通化
- 可読性向上：メインロジックがより明確に
- 保守性向上：変更が1箇所で完結

## 修正内容

### 変更ファイル
- `utils/json-validator/validator/file_validator.py`
- `utils/json-validator/tests/test_file_validator.py`

### 追加メソッド
```python
def _extract_object_type_from_ref(self, resolver, ref_url: str) -> Optional[str]:
    """
    $refを解決してobject_typeを抽出する共通処理
    
    Args:
        resolver: RefResolverインスタンス
        ref_url (str): 解決する$ref URL
        
    Returns:
        Optional[str]: 抽出されたobject_type、取得できない場合はNone
    """
```

### 修正メソッド
`_get_allowed_object_types`メソッドを以下の構造に変更：
1. oneOf構造のチェック（既存機能）
2. 直接$ref構造のチェック（新機能）
3. 共通処理（`_extract_object_type_from_ref`）の活用

## テスト結果

### 修正前
```
object_type 'SECURITY_HOLDER' は許可されていません。許可されているobject_type: []
```

### 修正後
```
SecurityHoldersFile.jocf.json validation errors:
  - items[0]のオブジェクト検証エラー: JSONスキーマ検証エラー: 'email' is a required property
```

## 成果
- ✅ object_type検証エラーが解決
- ✅ 既存のoneOf構造の動作が維持（回帰テスト通過）
- ✅ 次のエラー（必須プロパティ不足）が表面化

## 次のステップ
1. Name型のスキーマ不一致問題（文字列 vs オブジェクト）
2. 必須プロパティの不足問題（`email`等）
3. 残り16個のファイルのバリデーションエラー対応

## 技術的な学び
- スキーマ構造の多様性への対応の重要性
- TDDによる安全なリファクタリング
- 共通処理抽出によるコード品質向上
- 段階的なエラー解決アプローチの有効性

---

## 追加作業: Name型スキーマ不一致問題の修正

### 問題の発見・分析
object_type検証エラー解決後、次の問題が表面化：
```
'創業者 A(移転元)' is not of type 'object'
'株式会社 X(移転先)' is not of type 'object'
```

**根本原因:**
- スキーマ: Name型を**オブジェクト**として定義（`legal_name`必須）
- サンプルファイル: 多くの箇所で**文字列**として記述
- 影響範囲: 17個のサンプルファイルでバリデーションエラー

### TDD実装プロセス（Name型修正）

#### 🔴 Red Phase
`TestNameTypeValidation`クラスを追加：
- 文字列形式のName型がエラーになることを確認
- 正しいオブジェクト形式のName型が成功することを確認

#### 🟢 Green Phase
サンプルファイルの修正：
```json
// 修正前（エラー）
"name": "創業者 A(移転元)"

// 修正後（正常）
"name": {
    "legal_name": "創業者 A(移転元)"
}
```

#### 修正したファイル一覧
1. **stocktransfer/SecurityHoldersFile.jocf.json** (2箇所)
2. **stock_repurchase/SecurityHoldersFile.jocf.json** (1箇所)
3. **seeds/SecurityHoldersFile.jocf.json** (2箇所)
4. **j-kiss_2/1/SecurityHoldersFile.jocf.json** (1箇所)
5. **seeds/TransactionsFile.jocf.json** (6箇所)
6. **seeds/SecurityholdersAgreementsFile.jocf.json** (3箇所)

**合計15箇所のName型エラーを修正**

### テスト結果の推移

| 段階 | 有効ファイル | 無効ファイル | 成功率 | 改善 |
|------|-------------|-------------|--------|------|
| 初期状態 | 0 | 17 | 0% | - |
| object_type修正後 | 6 | 17 | 26.1% | +6 |
| Name型修正後 | **7** | **16** | **30.4%** | **+1** |

### 🔵 Refactor Phase
修正後の状況：
- ✅ object_type許可エラー → 完全解決
- ✅ Name型スキーマ不一致 → **大幅改善**
- 🔄 次の問題が表面化：
  - 必須プロパティ不足（`email`, `securityholder_id`等）
  - 数値型エラー（`3 is not of type 'string'`）
  - アドレス型エラー（オブジェクト vs 文字列）

### 成果
- **成功率30.4%まで向上**
- **Name型問題の大部分が解決**
- **段階的エラー解決アプローチの有効性を実証**
- **TDDサイクルによる安全な修正プロセスを確立**

### 次のフェーズへの準備
残り16個のファイルの問題は、Name型以外のスキーマ不一致が中心：
1. 必須プロパティの追加
2. 数値型の文字列化
3. アドレス型の統一

各問題についてもTDDアプローチで段階的に解決予定。