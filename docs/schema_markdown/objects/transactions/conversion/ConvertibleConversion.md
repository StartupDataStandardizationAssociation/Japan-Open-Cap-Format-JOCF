# コンバーティブルエクイティ転換トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/conversion/ConvertibleConversion.schema.json`

## Description
コンバーティブルエクイティ転換トランザクション

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [Conversion](../../../primitives/objects/transactions/conversion/Conversion.md)
- [SecurityTransaction](../../../primitives/objects/transactions/SecurityTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_CONVERTIBLE_CONVERSION) | Yes |  |
| reason_text | string | Yes | 転換権の行使の理由 |
| quantity_converted | [Numeric](../../../types/Numeric.md) | No | 転換権が行使されたコンバーティブルエクイティの個数 |
| balance_security_id | string | No | 部分的な転換の場合に、転換せずに残る転換権の証券ID |
| trigger_id | string | Yes | 転換権の行使のトリガーとなったトリガーのID |
| id | - | Yes | 基底クラスから継承 |
| comments | - | No | 基底クラスから継承 |
| security_id | - | Yes | 基底クラスから継承 |
| date | - | Yes | 基底クラスから継承 |
| resulting_security_ids | - | Yes | 基底クラスから継承 |