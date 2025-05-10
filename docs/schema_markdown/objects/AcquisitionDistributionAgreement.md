# Object - Acquisition Distribution Agreement

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/AcquisitionDistributionAgreement.schema.json`

## Description
買収に係る分配に関する契約

## Composed from
- [Object](../primitives/objects/Object.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (ACQUISITION_DISTRIBUTION_AGREEMENT) | Yes |  |
| description | string | No | 買収に係る分配に関する契約の説明。 残余財産の分配の詳細については、StockClassのliquidation_preference_attributesを合わせて参照のこと。 |
| securityholders_who_agreed | array | No | 分配合意書に合意する証券保有者の一覧 |
| put_option_on_aquisition_attributes | object | No | 買収時の売却請求権に関する属性 |
| put_option_on_aquisition_attributes.has_put_option_on_aquisition | boolean | Yes | 買収時の売却請求権の有無 |
| put_option_on_aquisition_attributes.clause_text | string | No | 買収時の売却請求権に関する条文 |
| put_option_on_ipo_failure_attributes | object | No | IPOが期限までに実施されなかった場合の売却請求権に関する属性 |
| put_option_on_ipo_failure_attributes.has_put_option_on_ipo_failure | boolean | Yes | IPOが期限までに実施されなかった場合の売却請求権の有無 |
| put_option_on_ipo_failure_attributes.clause_text | string | No | IPOが期限までに実施されなかった場合の売却請求権に関する条文 |
| id | - | Yes | Objectから継承 |