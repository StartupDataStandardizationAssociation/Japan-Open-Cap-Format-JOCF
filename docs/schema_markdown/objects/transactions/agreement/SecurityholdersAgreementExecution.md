# Transaction - Securityholders Agreement Execution

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/agreement/SecurityholdersAgreementExecution.schema.json`

## Description
証券保有者間同意の成立に関するトランザクション

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [SecurityholdersAgreementTransaction](../../../primitives/objects/transactions/SecurityholdersAgreementTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_SECURITYHOLDERS_AGREEMENT_EXECUTION) | Yes |  |
| id | - | Yes | 基底クラスから継承 |
| date | - | Yes | 基底クラスから継承 |
| securityholders_agreement | - | Yes | 基底クラスから継承 |
| description | string | No | 証券保有者間同意の成立に関するトランザクションの説明 |