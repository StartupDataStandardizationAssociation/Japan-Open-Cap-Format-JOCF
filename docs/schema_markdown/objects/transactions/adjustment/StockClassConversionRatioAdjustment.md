# 株式クラスの転換比率の調整トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/adjustment/StockClassConversionRatioAdjustment.schema.json`

## Description
ダウンラウンドなどに起因した希薄化防止条項の発動による、優先株の転換比率の調整の発生を表現するトランザクション

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [StockClassTransaction](../../../primitives/objects/transactions/StockClassTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_CLASS_CONVERSION_RATIO_ADJUSTMENT) | Yes |  |
| id | - | Yes | 基底クラスから継承 |
| comments | - | No | 基底クラスから継承 |
| date | - | Yes | 基底クラスから継承 |
| stock_class_id | - | Yes | 基底クラスから継承 |
| adjusted_trigger_id | string | No | 調整対象のトリガーの識別子 |
| initial_trigger_id | string | No | 調整の起因となったトリガーの識別子 |
| new_ratio_conversion_mechanism | [RatioConversionMechanism](../../../types/conversion_mechanisms/RatioConversionMechanism.md) | Yes | 元の転換価額から新しい転換価額への変更に基づく新しい転換メカニズム |