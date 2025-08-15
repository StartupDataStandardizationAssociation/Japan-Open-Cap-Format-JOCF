# 20250703_2_numeric-type-validation-and-complex-schema-analysis.md

## 概要
Numeric型のスキーマ不一致問題をTDDで修正し、複雑なスキーマ検証エラー（oneOf validation失敗）について詳細調査を実施。

## 対応した問題

### 1. Numeric型エラーの発見
`utils/json-validator/tests/test_sample_files.py`実行時に以下のエラーが発生：
```
3 is not of type 'string'
```

### 2. 根本原因分析
- **スキーマ**: Numeric型を**文字列**として定義（パターン`^[+-]?[0-9]+(\\.[0-9]{1,10})?$`）
- **サンプルファイル**: **数値**として記述（`"seniority": 3`）
- **影響箇所**: `samples/seeds/StockClasssesFile.jocf.json`の97行目、103行目

### 3. 詳細調査結果
スキーマファイル分析により、2つの異なる`seniority`プロパティを発見：

1. **`dividend_attributes.seniority`**: `"type": "integer"` → **数値型が正しい**
2. **`liquidation_preference_attributes.seniority`**: `"$ref": "...Numeric.schema.json"` → **文字列型が正しい**

## TDD実装プロセス

### 🔴 Red Phase
`TestNumericTypeValidation`クラスを追加：
- 数値形式のNumeric型がエラーになることを確認
- 正しい文字列形式のNumeric型が成功することを確認

### 🟢 Green Phase
サンプルファイルの修正：
```json
// 修正前（エラー）
"seniority": 3

// 修正後（正常）
"dividend_attributes": {
    "seniority": 3  // integer型として維持
},
"liquidation_preference_attributes": {
    "seniority": "3"  // Numeric型（文字列）に修正
}
```

### 修正内容
**ファイル**: `samples/seeds/StockClasssesFile.jocf.json`
- **97行目**: `dividend_attributes.seniority` → 数値`3`を維持（integer型）
- **103行目**: `liquidation_preference_attributes.seniority` → 文字列`"3"`に修正（Numeric型）

### テスト結果
**修正前のエラー:**
```
3 is not of type 'string'
'3' is not of type 'integer'
```

**修正後:**
Numeric型エラーが完全に解決され、次の問題が表面化

### 🔵 Refactor Phase
- ✅ Numeric型問題の完全解決
- ✅ スキーマ定義と実装の整合性確保
- 🔄 より複雑なスキーマ検証エラーが表面化

## 複雑なスキーマ検証エラーの詳細調査

### 新たに発見されたエラー
```
not valid under any of the given schemas
```

### エラーの詳細分析

#### 1. 問題の箇所
- **ファイル**: `samples/seeds/StockClasssesFile.jocf.json`
- **オブジェクト**: `conversion_triggers[2]` (ANTI_DILUTION_PROTECTION)
- **スキーマ**: oneOf検証で全ての候補スキーマが失敗

#### 2. oneOfスキーマ候補
1. `ElectiveConversionAtWillTrigger.schema.json`
2. `AntiDilutionProtectionTrigger.schema.json`
3. `AutomaticConversionOnConditionTrigger.schema.json`

#### 3. 問題のオブジェクト構造
```json
{
  "type": "ANTI_DILUTION_PROTECTION",
  "nickname": "分割・併合・無償割り当てに関する希薄化防止条項",
  "anti_dilution_protection_type": "BROAD_BASED_WEIGHTED_AVERAGE",
  "conversion_right": {
    "type": "STOCK_CLASS_CONVERSION_RIGHT",
    "conversion_mechanism": {
      "type": "RATIO_CONVERSION",
      "conversion_price": {"amount": "0", "currency": "JPY"},
      "ratio": "1",
      "rounding_type": "FLOOR"
    },
    "converts_to_future_round": true
  }
}
```

#### 4. 型検証結果
- **converts_to_future_round**: `true` (JSON boolean) ✅
- **スキーマ定義**: `"type": "boolean"` ✅
- **Python型**: `<class 'bool'>` ✅

**→ boolean型自体は正しい**

#### 5. 想定される問題
1. **conversion_mechanismの詳細仕様不一致**
2. **必須プロパティの不足**
3. **additionalProperties制約違反**
4. **RatioConversionMechanism.schema.json内の制約**

#### 6. 影響範囲
同様の問題があるファイル：
- `samples/StockClassesFile.jocf.json`
- `samples/cases/dilution-protection/1/StockClassesFile.jocf.json`
- `samples/cases/dilution-protection/2/StockClassesFile.jocf.json`
- `samples/j-kiss_2/1/TransactionsFile.jocf.json`

## 全体進捗の推移

| 段階 | 有効ファイル | 無効ファイル | 成功率 | 主な解決問題 |
|------|-------------|-------------|--------|-------------|
| 初期状態 | 0 | 17 | 0% | - |
| object_type修正後 | 6 | 17 | 26.1% | 直接$ref構造対応 |
| Name型修正後 | 7 | 16 | 30.4% | Name型オブジェクト化 |
| **Numeric型修正後** | **7** | **16** | **30.4%** | **Numeric型文字列化** |

### 解決済み問題
1. ✅ object_type許可エラー → 完全解決
2. ✅ Name型スキーマ不一致 → 大幅改善
3. ✅ **Numeric型エラー → 完全解決**

### 残りの問題（優先度順）
1. **複雑なスキーマ検証エラー** (高優先度)
   - oneOf validation失敗
   - conversion_triggers構造の不一致
2. **アドレス型エラー** (中優先度)
   - オブジェクト vs 文字列の型不一致
3. **必須プロパティ不足** (低優先度)

## 技術的な学び
- **スキーマの複雑性**: 同名プロパティでも文脈により型が異なる場合の対応
- **段階的エラー解決**: 単純なエラーから複雑なエラーへの段階的な解決プロセス
- **oneOfスキーマの複雑性**: 複数候補スキーマでの検証失敗の診断の困難さ
- **TDDアプローチの有効性**: 特定の問題を確実に解決し、次の問題を表面化

## 次のフェーズへの準備
複雑なスキーマ検証エラーの解決には以下の詳細調査が必要：
1. **RatioConversionMechanism.schema.json**の詳細分析
2. **AntiDilutionProtectionTrigger**の必須プロパティ確認
3. **oneOf各候補での具体的な検証失敗理由の特定**
4. **additionalProperties制約の確認**

この問題は構造全体の整合性に関わる複雑な課題であり、慎重なスキーマ分析が必要。