# 株式転換トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/conversion/StockConversion.schema.json`

## Description
株式転換トランザクション

## Composed from
- [Object](../../../primitive/objects/Object.md)
- [Transaction](../../../primitive/objects/transactions/Transaction.md)
- [Conversion](../../../primitive/objects/transactions/conversion/Conversion.md)
- [SecurityTransaction](../../../primitive/objects/transactions/SecurityTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_CONVERTIBLE_CONVERSION) | Yes |  |
| quantity_converted | [Numeric](../../../types/Numeric.md) | Yes | 転換された株式数 |
| stock_class_id_converted | [Numeric](../../../types/Numeric.md) | Yes | 転換された株式種類のID |
| quantity | [Numeric](../../../types/Numeric.md) | Yes | 転換後の株式数 |
| stock_class_id | [Numeric](../../../types/Numeric.md) | Yes | 転換後の株式種類のID |
| id | - | Yes | 基底クラスから継承 |
| description | - | No | 基底クラスから継承 |
| date | - | Yes | 基底クラスから継承 |
| security_id | - | Yes | 基底クラスから継承 |
| resulting_security_ids | - | Yes | 基底クラスから継承 |
| comments | - | No | 基底クラスから継承 |