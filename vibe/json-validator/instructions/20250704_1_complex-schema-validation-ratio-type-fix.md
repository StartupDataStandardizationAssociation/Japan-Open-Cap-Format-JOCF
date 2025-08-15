# 20250704_1_complex-schema-validation-ratio-type-fix.md

## 概要
複雑なスキーマ検証エラー（oneOf validation失敗）の根本原因を特定し、TDDアプローチでRatio型の修正を実施。成功率を30.4%から34.8%に向上。

## 問題の発見と分析

### 発見されたエラー
`utils/json-validator/tests/test_sample_files.py`実行時に以下のエラーが発生：
```
not valid under any of the given schemas
```

### 詳細調査結果

#### oneOfスキーマ検証失敗
**問題の箇所**: `conversion_triggers[2]` (ANTI_DILUTION_PROTECTION)
**oneOF候補スキーマ**:
1. `ElectiveConversionAtWillTrigger.schema.json`
2. `AntiDilutionProtectionTrigger.schema.json`
3. `AutomaticConversionOnConditionTrigger.schema.json`

#### 根本原因の特定
**conversion_mechanismの型不一致**:
```json
// 実際のデータ（問題）
{
  "type": "RATIO_CONVERSION",
  "conversion_price": {"amount": "0", "currency": "JPY"},
  "ratio": "1",  // ❌ 文字列
  "rounding_type": "FLOOR"
}

// RatioConversionMechanism.schema.jsonが期待する形式
{
  "type": "RATIO_CONVERSION", 
  "conversion_price": {"amount": "0", "currency": "JPY"},
  "ratio": {     // ❌ Ratio型オブジェクトが必要
    "numerator": "1",    // Numeric型（文字列）
    "denominator": "1"   // Numeric型（文字列）
  },
  "rounding_type": "FLOOR"
}
```

### スキーマ構造の詳細分析

#### RatioConversionMechanism.schema.json
- **必須プロパティ**: `["ratio", "conversion_price", "rounding_type", "type"]`
- **additionalProperties**: `false`
- **ratio**: `Ratio.schema.json`を参照

#### Ratio.schema.json
```json
{
  "type": "object",
  "properties": {
    "numerator": {"$ref": "...Numeric.schema.json"},
    "denominator": {"$ref": "...Numeric.schema.json"}
  },
  "required": ["numerator", "denominator"]
}
```

### 影響範囲の特定
同様の問題があるファイル：
1. `samples/seeds/StockClasssesFile.jocf.json` (3箇所)
2. `samples/StockClassesFile.jocf.json` (2箇所)
3. `samples/cases/dilution-protection/1/StockClassesFile.jocf.json` (1箇所)
4. `samples/cases/dilution-protection/2/StockClassesFile.jocf.json` (1箇所)

## TDD実装プロセス

### 🔴 Red Phase
`TestConversionMechanismValidation`クラスを追加：

```python
def test_ratio_field_should_be_object_not_string(self):
    """ratio フィールドは文字列ではなくオブジェクトであるべき - 現在失敗する"""
    conversion_mechanism_data = {
        "ratio": "1",  # 問題: 文字列形式
        # ...
    }
    # oneOf検証エラーの確認

def test_ratio_field_correct_object_format(self):
    """正しいオブジェクト形式のratio型は検証に通るべき"""
    conversion_mechanism_data = {
        "ratio": {  # 正しい: オブジェクト形式
            "numerator": "1",
            "denominator": "1"
        },
        # ...
    }
    # 検証成功の確認
```

### 🟢 Green Phase
**修正内容**:
```json
// 修正前（エラー）
"ratio": "1"

// 修正後（正常）
"ratio": {
    "numerator": "1",
    "denominator": "1"
}
```

**修正したファイルと箇所**:
1. **seeds/StockClasssesFile.jocf.json**: 3箇所修正
2. **StockClassesFile.jocf.json**: 2箇所修正
3. **cases/dilution-protection/1/StockClassesFile.jocf.json**: 1箇所修正
4. **cases/dilution-protection/2/StockClassesFile.jocf.json**: 1箇所修正

### 🔵 Refactor Phase
- ✅ 複雑なスキーマ検証エラーの完全解決
- ✅ oneOf validation成功
- ✅ RatioConversionMechanism.schema.jsonとの完全整合性確保

## テスト結果

### 修正前のエラー
```
not valid under any of the given schemas
Seeds files summary: 2 valid, 2 invalid
```

### 修正後の改善
```
Seeds files summary: 3 valid, 1 invalid
```

**🎯 StockClasssesFile.jocf.jsonの複雑なスキーマ検証エラーが完全に解決！**

## 全体進捗の推移

| 段階 | 有効ファイル | 無効ファイル | 成功率 | 改善度 | 主な解決問題 |
|------|-------------|-------------|--------|--------|-------------|
| 初期状態 | 0 | 17 | 0% | - | - |
| object_type修正後 | 6 | 17 | 26.1% | +6 | 直接$ref構造対応 |
| Name型修正後 | 7 | 16 | 30.4% | +1 | Name型オブジェクト化 |
| Numeric型修正後 | 7 | 16 | 30.4% | +0 | Numeric型文字列化 |
| **Ratio型修正後** | **8** | **15** | **34.8%** | **+1** | **oneOf validation成功** |

### カテゴリ別改善状況
- **ケース**: 11ファイル (有効: 4, 無効: 7) - 36.4%
- **J-KISS**: 4ファイル (有効: 1, 無効: 3) - 25.0%  
- **シード**: 4ファイル (有効: 3, 無効: 1) - **75.0%** 🎉
- **株式買い戻し**: 2ファイル (有効: 0, 無効: 2) - 0%
- **株式譲渡**: 2ファイル (有効: 0, 無効: 2) - 0%

## 解決済み問題一覧

### ✅ 完全解決済み
1. **object_type許可エラー** → 直接$ref構造対応により解決
2. **Name型スキーマ不一致** → オブジェクト形式への修正により大幅改善
3. **Numeric型エラー** → 文字列/数値の適切な使い分けにより解決
4. **複雑なスキーマ検証エラー（ratio型）** → Ratioオブジェクト化により解決

### 🔄 残りの問題（優先度順）
1. **アドレス型エラー** (最優先)
   ```
   {'postal_code': '100-0001', ...} is not of type 'string'
   ```
2. **必須プロパティ不足** (中優先度)
3. **その他の構造的不一致** (低優先度)

## 技術的な学び

### スキーマ設計の複雑性
- **oneOfパターン**: 複数の候補スキーマから1つを選択する高度な検証メカニズム
- **ネストしたオブジェクト型**: Ratio型のようなネストした構造での型整合性の重要性
- **参照解決の連鎖**: $ref → Ratio.schema.json → Numeric.schema.json の多層参照

### TDDアプローチの有効性
- **段階的解決**: 個別の問題を確実に解決し、次の問題を表面化させるアプローチ
- **回帰防止**: 既存の修正が壊れないことをテストで保証
- **明確な進捗**: 成功率という客観的指標での改善度測定

### JSON スキーマ検証の深さ
- **型の厳密性**: 文字列 vs オブジェクトの区別の重要性
- **構造の整合性**: プロパティの存在だけでなく、ネストした構造まで検証
- **additionalProperties制約**: 予期しないプロパティの検出

## 次のフェーズへの準備

**34.8%の成功率**達成により、基本的なスキーマ不一致問題の大部分を解決。

**次の焦点**:
1. **アドレス型エラー**: オブジェクト vs 文字列の型不一致
2. **必須プロパティ補完**: スキーマが要求する必須プロパティの追加
3. **最終的な構造整合性**: 残り15ファイルの完全な適合性確保

**目標**: 成功率50%以上を目指し、JOCFサンプルファイルの品質向上を継続。