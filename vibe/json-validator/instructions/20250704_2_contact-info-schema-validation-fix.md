# 20250704_2_contact-info-schema-validation-fix.md

## 概要
SecurityHolderContactInfoスキーマ不一致エラーをTDDアプローチで解決し、成功率を43.5%に向上。「アドレス型エラー」として認識されていた問題の真の原因を特定し、必須プロパティ不一致問題を完全解決。

## 問題の発見と分析

### 発見されたエラー
`utils/json-validator/tests/test_sample_files.py`実行時に以下のエラーが発生：
```
'email' is a required property
```

### 詳細調査結果

#### 真の問題の特定
**文書記載の「postal_code型エラー」は実際には別の問題でした**：

```
Failed validating 'required' in schema['properties']['contact_info']['items']:
    {'$id': 'https://jocf.startupstandard.org/jocf/main/schema/types/SecurityHolderContactInfo.schema.json',
     'required': ['email']}

On instance['contact_info'][0]:
    {'phone_numbers': [{'phone_number': '03-1234-5678', 'phone_type': 'BUSINESS'}],
     'emails': [{'email_address': 'test@example.com', 'email_type': 'BUSINESS'}]}
```

#### 根本原因の特定
**SecurityHolderContactInfoスキーマの必須プロパティ不一致**：
```json
// SecurityHolderContactInfo.schema.json（問題）
{
  "properties": {
    "phone_numbers": { ... },
    "emails": { ... }  // ✅ 'emails'配列は定義されている
  },
  "required": ["email"]  // ❌ 'email'が必須だが実際は'emails'配列
}

// 実際のサンプルファイル構造
{
  "contact_info": [{
    "phone_numbers": [...],
    "emails": [...]  // ✅ 'emails'配列は存在
    // ❌ 'email'プロパティは存在しない
  }]
}
```

### 影響範囲の特定
**2つのスキーマファイルで同じ問題**：
1. `SecurityHolderContactInfo.schema.json:24` - `"required": ["email"]`
2. `SecurityHolderPrimaryContact.schema.json:29` - `"required": ["name", "email"]`

**影響を受けるサンプルファイル**：
- `samples/stock_repurchase/SecurityHoldersFile.jocf.json`
- `samples/stocktransfer/SecurityHoldersFile.jocf.json`
- `samples/cases/securityholders-agreement/1/SecurityHoldersFile.jocf.json`
- `samples/cases/securityholders-agreement/2/SecurityHoldersFile.jocf.json`
- `samples/SecurityHoldersFile.jocf.json`

## TDD実装プロセス

### 🔴 Red Phase
`TestContactInfoValidation`クラスを追加：

```python
def test_contact_info_required_field_mismatch(self):
    """🔴 Red: 現在のスキーマエラーを再現 - emailフィールドが存在しない"""
    contact_info_data = {
        "phone_numbers": [{"phone_number": "03-1234-5678", "phone_type": "BUSINESS"}],
        "emails": [{"email_address": "test@example.com", "email_type": "BUSINESS"}]
        # ❌ 'email'プロパティは存在しない
    }
    # ValidationError("'email' is a required property")の確認

def test_contact_info_with_correct_structure(self):
    """🔴 Red: 正しい構造での検証成功を確認"""
    corrected_schema = {
        "required": ["emails"]  # ✅ 修正: 'email' → 'emails'
    }
    # 検証成功の確認
```

### 🟢 Green Phase
**最小限のスキーマ修正**：

#### 1. SecurityHolderContactInfo.schema.json修正
```json
// 修正前（エラー）
"required": ["email"]

// 修正後（正常）
"required": ["emails"]
```

#### 2. SecurityHolderPrimaryContact.schema.json修正
```json
// 修正前（エラー）
"required": ["name", "email"]

// 修正後（正常）
"required": ["name", "emails"]
```

### 🔵 Refactor Phase
- ✅ SecurityHolderContactInfoエラーの完全解決
- ✅ 必須プロパティ不一致問題の根本解決
- ✅ 全サンプルファイルとの整合性確保

## 実際のデータ構造分析

### 100%一貫したパターン
**全サンプルファイルで同じ構造を使用**：
```json
"contact_info": [
    {
        "phone_numbers": [
            {
                "phone_number": "03-1234-5678",
                "phone_type": "BUSINESS"
            }
        ],
        "emails": [
            {
                "email_address": "test@example.com",
                "email_type": "BUSINESS"
            }
        ]
    }
]
```

### スキーマ vs 現実の不一致
- **スキーマ期待**: `"email"` (単数、存在しない)
- **実際の構造**: `"emails"` (複数、配列)
- **スキーマ定義**: `"emails"` プロパティは正しく定義済み
- **required不一致**: 存在しない`"email"`を必須指定

## テスト結果

### 修正前のエラー
```
成功率: 34.8% (8 valid, 15 invalid)
'email' is a required property
```

### 修正後の改善
```
成功率: 43.5% (10 valid, 13 invalid)
```

**🎯 SecurityHolderContactInfo関連エラーが完全に解決！**

## 全体進捗の推移

| 段階 | 有効ファイル | 無効ファイル | 成功率 | 改善度 | 主な解決問題 |
|------|-------------|-------------|--------|--------|-------------|
| 初期状態 | 0 | 17 | 0% | - | - |
| object_type修正後 | 6 | 17 | 26.1% | +6 | 直接$ref構造対応 |
| Name型修正後 | 7 | 16 | 30.4% | +1 | Name型オブジェクト化 |
| Numeric型修正後 | 7 | 16 | 30.4% | +0 | Numeric型文字列化 |
| Ratio型修正後 | 8 | 15 | 34.8% | +1 | oneOf validation成功 |
| **ContactInfo修正後** | **10** | **13** | **43.5%** | **+2** | **必須プロパティ不一致解決** |

### カテゴリ別改善状況
- **ケース**: 11ファイル (有効: 4, 無効: 7) - 36.4%
- **J-KISS**: 4ファイル (有効: 1, 無効: 3) - 25.0%
- **シード**: 4ファイル (有効: 3, 無効: 1) - 75.0%
- **株式買い戻し**: 2ファイル (有効: 1, 無効: 1) - **50.0%** (0%から大幅改善 🎉)
- **株式譲渡**: 2ファイル (有効: 1, 無効: 1) - **50.0%** (0%から大幅改善 🎉)

## 解決済み問題一覧

### ✅ 完全解決済み
1. **object_type許可エラー** → 直接$ref構造対応により解決
2. **Name型スキーマ不一致** → オブジェクト形式への修正により大幅改善
3. **Numeric型エラー** → 文字列/数値の適切な使い分けにより解決
4. **複雑なスキーマ検証エラー（ratio型）** → Ratioオブジェクト化により解決
5. **SecurityHolderContactInfo必須プロパティ不一致** → requiredフィールド修正により解決

### 🔄 残りの問題（優先度順）
1. **その他の必須プロパティ不足** (高優先度)
2. **型不一致エラー** (中優先度)
3. **構造的不一致** (低優先度)

## 技術的な学び

### スキーマ設計の重要性
- **required配列の整合性**: プロパティ定義と必須フィールドの一致確認の重要性
- **実データとの整合性**: サンプルファイルとスキーマ定義の継続的な検証
- **命名規則の一貫性**: 単数形 vs 複数形の統一的なルール適用

### TDDアプローチの有効性
- **問題の本質特定**: 表面的なエラーメッセージから真の原因を特定
- **最小限の修正**: 2ファイル、計2行の変更で+8.7%の改善
- **回帰防止**: テストケース作成による将来的な問題防止

### 調査手法の改善
- **エラーメッセージの正確な解釈**: 「アドレス型エラー」→「必須プロパティ不一致」
- **全体像の把握**: 個別ファイルではなくパターン全体の分析
- **データ駆動の意思決定**: 100%のサンプルファイルで一貫したパターンを確認

## 次のフェーズへの準備

**43.5%の成功率**達成により、基本的なスキーマ不一致問題の大部分を解決。

**次の焦点**:
1. **残りの必須プロパティ問題**: 他の不足している必須フィールドの特定と修正
2. **型不一致の詳細分析**: 残り13ファイルの具体的なエラー内容の調査
3. **最終的な構造整合性**: 全23ファイルの完全な適合性確保

**目標**: 成功率50%以上を目指し、JOCFサンプルファイルの品質向上を継続。

## 次のタスク候補

1. **必須プロパティエラーの網羅的調査**: 残り13ファイルの詳細エラー分析
2. **型不一致パターンの特定**: 文字列 vs オブジェクト、数値 vs 文字列等の整理
3. **スキーマ全体の整合性チェック**: 他の型定義での同様の問題の洗い出し