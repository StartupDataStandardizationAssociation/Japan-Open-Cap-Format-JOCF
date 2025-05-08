# Type - コンバーティブルエクイティの転換権

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/conversion_rights/ConvertibleConversionRight.schema.json`

## Description
コンバーティブルエクイティの株式クラスへの転換権を表現するクラス

## Composed from
- [ConversionRight](../../../../primitives/types/conversion_rights/ConversionRight.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | const (CONVERTIBLE_CONVERSION_RIGHT) | Yes |  |
| conversion_mechanism | unknown | Yes |  |
| converts_to_future_round | unknown | No |  |
| converts_to_stock_class_id | unknown | No |  |