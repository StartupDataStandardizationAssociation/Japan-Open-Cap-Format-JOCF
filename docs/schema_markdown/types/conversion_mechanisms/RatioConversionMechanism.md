# Conversion Mechanism - Ratio

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/conversion_mechanisms/RatioConversionMechanism.schema.json`

## Description
比率による転換メカニズムを設定します（例えば、優先株から普通株式への転換を記述するために使用されます)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | const (RATIO_CONVERSION) | Yes |  |
| description | string | No | 転換メカニズムの説明 |
| conversion_price | [Monetary](../../types/Monetary.md) | Yes | 株式の1株当たりの転換価格 |
| ratio | [Ratio](../../types/Ratio.md) | Yes | 転換比率 |
| rounding_type | [RoundingType](../../enums/RoundingType.md) | Yes | 転換時の丸め方 |