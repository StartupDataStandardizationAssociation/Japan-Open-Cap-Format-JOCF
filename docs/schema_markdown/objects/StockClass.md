# 株式種類

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json`

## Composed from
- [Object](../primitives/objects/Object.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (STOCK_CLASS) | Yes |  |
| name | string | Yes | 株式種類名 |
| id | string | Yes | 株式種類のID |
| description | string | No | 株式種類の説明 |
| class_type | [StockClassType](../enums/StockClassType.md) | Yes | 株式種類のタイプ（例. 普通、もしくは優先） |
| votes_per_share | [Numeric](../types/Numeric.md) | No | 一株あたりの議決権(株主総会) |
| votes_per_share_at_class_meeting | [Numeric](../types/Numeric.md) | No | 一株あたりの議決権(種類株主総会) |
| initial_shares_authorized | one of: <br> - [AuthorizedShares](../types/AuthorizedShares.md)<br> - [Numeric](../types/Numeric.md) | No | 株式発行時点での種類株式の発行可能株式数 |
| preffered_stock_attributes | object | No | 優先株の発行に関する項目 |
| preffered_stock_attributes.conversion_triggers | one of: <br> - [ElectiveConversionAtWillTrigger](../types/conversion_triggers/ElectiveConversionAtWillTrigger.md)<br> - [AntiDilutionProtectionInDownRoundTrigger](../types/conversion_triggers/AntiDilutionProtectionInDownRoundTrigger.md)<br> - [AutomaticConversionOnConditionTrigger](../types/conversion_triggers/AutomaticConversionOnConditionTrigger.md) | Yes | 優先株が持つ転換条件一覧 |
| preffered_stock_attributes.dividend_attributes | object | No | 配当に関する項目 |
| preffered_stock_attributes.dividend_attributes.dividend_rate | [Numeric](../types/Numeric.md) | No | 配当率(年率) |
| preffered_stock_attributes.dividend_attributes.participation_category | [ParticipationCategory](../enums/ParticipationCategory.md) | No | 配当参加型区分 |
| preffered_stock_attributes.dividend_attributes.cumulative_category | [CumulativeCategory](../enums/CumulativeCategory.md) | No | 配当累積区分 |
| preffered_stock_attributes.dividend_attributes.seniority | integer | No | 配当順位 |
| preffered_stock_attributes.liquidation_preference_attributes | object | No | 清算時の残余財産分配の優先権に関する項目 |
| preffered_stock_attributes.liquidation_preference_attributes.liquidation_preference_multiple | [Numeric](../types/Numeric.md) | No | 残余財産分配倍率 |
| preffered_stock_attributes.liquidation_preference_attributes.participation_category | [ParticipationCategory](../enums/ParticipationCategory.md) | No | 清算時の残余財産分配の参加型区分 |
| preffered_stock_attributes.liquidation_preference_attributes.cumulative_category | [CumulativeCategory](../enums/CumulativeCategory.md) | No | 清算時の残余財産分配の累積区分 |
| preffered_stock_attributes.liquidation_preference_attributes.seniority | [Numeric](../types/Numeric.md) | No | 残余財産分配順位 |
| preffered_stock_attributes.redemption_right_attributes | object | No | 償還請求権に関する項目 |
| preffered_stock_attributes.redemption_right_attributes.redemption_trigger | string | No | 償還請求権が行使可能となる条件 |
| preffered_stock_attributes.redemption_right_attributes.redemption_formula | string | No | 償還額を決定する計算式 |
| preffered_stock_attributes.mandatory_conversion_attributes | object | No | 強制転換条項に関する項目 |
| preffered_stock_attributes.mandatory_conversion_attributes.mandatory_conversion_trigger | string | No | 強制転換条項が行使可能となる条件を記述する法的文言 |
| preffered_stock_attributes.mandatory_conversion_attributes.mandatory_conversion_formula | string | No | 強制転換額を決定する計算式を記述する法的文言 |
| preffered_stock_attributes.has_transfer_restrictions | boolean | No | 譲渡制限の有無 |