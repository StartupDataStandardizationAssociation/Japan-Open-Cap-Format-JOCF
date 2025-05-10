# Transaction - Securityholders Agreement Modification

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/agreement/SecurityholdersAgreementModification.schema.json`

## Description
証券保有者間同意の改定に関するトランザクション

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [SecurityholdersAgreementTransaction](../../../primitives/objects/transactions/SecurityholdersAgreementTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_SECURITYHOLDERS_AGREEMENT_MODIFICATION) | Yes |  |
| reason_text | string | No | 証券保有者間同意の改定の理由 |
| id | - | Yes | 基底クラスから継承 |
| date | - | Yes | 基底クラスから継承 |
| securityholders_agreement | - | Yes | 基底クラスから継承 |