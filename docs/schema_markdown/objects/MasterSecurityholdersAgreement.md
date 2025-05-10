# Object - Master of Securityholders Agreement

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/MasterSecurityholdersAgreement.schema.json`

## Description
証券保有者間同意における基本契約

## Composed from
- [Object](../primitives/objects/Object.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (MASTER_SECURITYHOLDERS_AGREEMENT) | Yes |  |
| securityholders_who_agreed | array | No | 証券保有者間基本契約に合意する証券保有者の一覧 |
| parties_and_authority_attributes | array | No | 証券保有者間同意における当事者の一覧とその権限属性 |
| obligation_to_provide_financial_information | array | No | 財務情報等の提供の義務 |
| right_to_access_financial_information | boolean | No | 財務情報の閲覧謄写検査請求権 |
| obligation_to_provide_material_information | array | No | 発行会社の重要情報提供義務 |
| obligation_of_managing_securityholder_to_fully_commit | array | No | 経営株主の経営専念義務 |
| preemptive_right | string | No | 株式等の優先引受権に関する法的文言 |
| right_of_first_refusal | string | No | 株式等の先買権に関する法的文言 |
| transfer_restrictions_on_securityholder | string | No | 証券保有者の譲渡制限に関する法的文言 |
| drag_along_right | string | No | 株式等の売却強制権に関する法的文言 |
| obligation_to_make_best_efforts_to_pursue_ipo | string | No | 株式公開を目指す努力義務に関する法的文言 |
| id | - | Yes | Objectから継承 |