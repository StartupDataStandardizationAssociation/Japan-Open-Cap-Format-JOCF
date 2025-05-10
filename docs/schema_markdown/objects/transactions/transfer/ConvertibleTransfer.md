# Object - Convertible Transfer Transaction

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/transfer/ConvertibleTransfer.schema.json`

## Description
コンバーティブルエクイティの所有権移転や売買を表現するトランザクション

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [SecurityTransaction](../../../primitives/objects/transactions/SecurityTransaction.md)
- [Transfer](../../../primitives/objects/transactions/transfer/Transfer.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_CONVERTIBLE_TRANSFER) | Yes |  |
| amount | [Monetary](../../../types/Monetary.md) | Yes | 移転の対象となる金額 |
| id | - | Yes | 基底クラスから継承 |
| comments | - | No | 基底クラスから継承 |
| security_id | - | Yes | 基底クラスから継承 |
| date | - | Yes | 基底クラスから継承 |
| consideration_text | - | No | 基底クラスから継承 |
| balance_security_id | - | No | 基底クラスから継承 |
| resulting_security_ids | - | Yes | 基底クラスから継承 |