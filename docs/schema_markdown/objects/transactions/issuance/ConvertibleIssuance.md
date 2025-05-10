# コンバーティブルエクイティ発行トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/ConvertibleIssuance.schema.json`

## Description
コンバーティブルエクイティ発行トランザクション

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [Issuance](../../../primitives/objects/transactions/issuance/Issuance.md)
- [SecurityTransaction](../../../primitives/objects/transactions/SecurityTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_CONVERTIBLE_ISSUANCE) | Yes |  |
| investment_amount | [Monetary](../../../types/Monetary.md) | Yes | 発行されたコンバーティブルエクイティに対する総投資額 |
| investment_amount_per_quantity | [Monetary](../../../types/Monetary.md) | No | 1コンバーティブルエクイティあたりの投資額 |
| quantity | [Numeric](../../../types/Numeric.md) | No | 発行されるコンバーティブルエクイティの個数 |
| convertible_type | [ConvertibleType](../../../enums/ConvertibleType.md) | Yes | 発行されたコンバーティブルエクイティの種類 |
| description | string | No | 説明 |
| seniority | integer | Yes | 配当順位 |
| seniority_clause | string | No | 配当順位。当該新コンバーチブルエクイティの配当順位を記述する法的な文言 |
| conversion_triggers | one of: <br> - [AutomaticConversionOnConditionTrigger](../../../types/conversion_triggers/AutomaticConversionOnConditionTrigger.md) | No | コンバーティブルエクイティの行使に関する条件の一覧 |
| series_name | string | No | コンバーティブルエクイティ発行シリーズ名 |
| public_template_integrity_clause | string | No | 本契約が公開されたテンプレートの保全に関する条項 |
| participation_cap_multiple | [Ratio](../../../types/Ratio.md) | No | 参加上限額倍率 |
| investor_roles_and_authorities | array of object | No | 投資家の種類と権限 |
| investor_roles_and_authorities.investor_type_name | string | No | 投資家の種類名 |
| investor_roles_and_authorities.investor_type_condition | string | No | 当該投資家種類とみなされるための条件 |
| investor_roles_and_authorities.information_request_rights | string | No | 当該投資家種類が持つ情報請求権 |
| investor_roles_and_authorities.preemptive_rights | string | No | 当該投資家種類が持つ優先引受権 |
| representations_and_warranties_by_issuing_company | [IssuerRepresentationsAndWarranties](../../../types/IssuerRepresentationsAndWarranties.md) | No | 発行会社による表明および保証 |
| self_representations_and_warranties_by_investor | [InvestorSelfRepresentationsAndWarranties](../../../types/InvestorSelfRepresentationsAndWarranties.md) | No | 投資家による発行会社に対する投資家自身に関する事項の表明および保証 |
| has_most_favored_nation_clause | boolean | No | 最恵待遇条項の有無 |
| transfer_restrictions_on_securityholder | string | No | 証券保有者の譲渡制限に関する法的文言 |
| obligation_of_investor_to_cooperate_on_amendment | string | No | 投資家の投資契約の変更及び放棄への協力義務 |
| exercise_price | [Monetary](../../../types/Monetary.md) | No | コンバーティブルエクイティ1個あたりの行使時払込額 |
| payment_due_date | string | No | 払込期日 |
| issuance_date | string | No | 割当日 |
| mandatory_redemption_attributes | object | No | 発行体の強制償還義務に関する項目 |
| mandatory_redemption_attributes.has_mandatory_redemption_trigger | boolean | Yes | 強制償還条件。強制償還条項が発動する条件の有無 |
| mandatory_redemption_attributes.mandatory_redemption_multiple | [Ratio](../../../types/Ratio.md) | No | 強制償還倍率。発行体は、コンバーティブルエクイティ1個ごとに、発行価額に対して当該倍率をかけた金額を支払う。 |
| id | - | Yes | 基底クラスから継承 |
| comments | - | No | 基底クラスから継承 |
| date | - | Yes | 基底クラスから継承 |
| securityholder_id | - | Yes | 基底クラスから継承 |
| security_id | - | Yes | 基底クラスから継承 |