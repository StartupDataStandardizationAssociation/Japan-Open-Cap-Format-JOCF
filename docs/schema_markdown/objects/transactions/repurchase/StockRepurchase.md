# Object - Stock Repurchase Transaction

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/repurchase/StockRepurchase.schema.json`

## Description
自社株買いを表現するトランザクション

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [SecurityTransaction](../../../primitives/objects/transactions/SecurityTransaction.md)
- [Repurchase](../../../primitives/objects/transactions/repurchase/Repurchase.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_REPURCHASE) | No |  |
| id | - | No | 基底クラスから継承 |
| comments | - | No | 基底クラスから継承 |
| security_id | - | No | 基底クラスから継承 |
| date | - | No | 基底クラスから継承 |
| price | - | No | 基底クラスから継承 |
| quantity | - | No | 基底クラスから継承 |
| consideration_text | - | No | 基底クラスから継承 |
| balance_security_id | - | No | 基底クラスから継承 |