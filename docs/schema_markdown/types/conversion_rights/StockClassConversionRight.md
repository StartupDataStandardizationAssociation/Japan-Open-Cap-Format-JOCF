# Type - Stock Class Conversion Rights

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/conversion_rights/StockClassConversionRight.schema.json`

## Description
ある株式クラスから別の株式クラスへの転換を表現するもの

## Composed from
- [ConversionRight](../../../primitives/types/conversion_rights/ConversionRight.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | const (STOCK_CLASS_CONVERSION_RIGHT) | Yes |  |
| conversion_mechanism | unknown | Yes |  |
| converts_to_future_round | unknown | No |  |
| converts_to_stock_class_id | unknown | No |  |