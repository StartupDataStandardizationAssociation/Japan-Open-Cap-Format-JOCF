# Primitive - Conversion Right Type

ID = `https://jocf.startupstandard.org/jocf/main/schema/primitives/types/conversion_rights/ConversionRight.schema.json`

## Description
転換権を表す基底クラス

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | [ConversionRightType](../../../enums/ConversionRightType.md) | Yes | 転換権の種別 |
| converts_to_future_round | boolean | No | 現時点で未確定な株式クラスに転換可能かどうか |
| converts_to_stock_class_id | string | No | 転換可能な既存の株式クラスのID |