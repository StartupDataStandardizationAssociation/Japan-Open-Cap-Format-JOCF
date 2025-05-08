# Conversion Mechanism - J-KISS

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/conversion_mechanisms/JKISSConversionMechanism.schema.json`

## Description
J-KISSによる転換メカニズムを表現します

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | const (J-KISS_CONVERSION) | Yes |  |
| description | string | No | 転換メカニズムの説明 |
| conversion_price_discount | [Percentage](../types/Percentage.md) | Yes | 本コンバーティブルエクイティの転換価格算出のために、転換価額決定対象の転換価額に対して適用するディスカウント。 J-KISS上の係数が0.8なら、本パラメータは0.2が設定される。 |
| minimum_equity_next_financing_threshold | [Monetary](../types/Monetary.md) | Yes | 転換価額決定の対象となる株式資金調達の最低調達額 |
| rounding_type | [RoundingType](../enums/RoundingType.md) | Yes | 転換時の丸め方 |
| money_valuation_cap | [Monetary](../types/Monetary.md) | Yes | プレキャップまたはポストキャップ。J-KISS 1.xではプレキャップ、J-KISS 2.xではポストキャップとなる。 |