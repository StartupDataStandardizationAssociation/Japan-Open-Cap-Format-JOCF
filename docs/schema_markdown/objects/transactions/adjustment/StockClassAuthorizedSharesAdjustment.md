# Object - 株式クラス発行可能株式調整トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/adjustment/StockClassAuthorizedSharesAdjustment.schema.json`

## Description
株式クラスの発行可能株式数を変更するためのイベント

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [StockClassTransaction](../../../primitives/objects/transactions/StockClassTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_CLASS_AUTHORIZED_SHARES_ADJUSTMENT) | No |  |
| id | - | No | 基底クラスから継承 |
| comments | - | No | 基底クラスから継承 |
| date | - | No | 基底クラスから継承 |
| stock_class_id | - | No | 基底クラスから継承 |
| new_shares_authorized | [Numeric](../../../types/Numeric.md) | Yes | 新しい発行可能株式数 |
| board_approval_date | [Date](../../../types/Date.md) | No | 取締役会承認日付 |
| stockholder_approval_date | [Date](../../../types/Date.md) | No | 株主承認日付 |