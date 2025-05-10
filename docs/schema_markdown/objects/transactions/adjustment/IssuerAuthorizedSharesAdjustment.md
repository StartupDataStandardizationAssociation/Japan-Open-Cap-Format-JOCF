# Object - Issuer Authorized Shares Adjustment Transaction

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/adjustment/IssuerAuthorizedSharesAdjustment.schema.json`

## Description
発行者レベルで認可された株式の数を変更するイベントを説明するオブジェクト。

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [IssuerTransaction](../../../primitives/objects/transactions/IssuerTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_ISSUER_AUTHORIZED_SHARES_ADJUSTMENT) | No |  |
| id | - | No | 基底クラスから継承 |
| comments | - | No | 基底クラスから継承 |
| date | - | No | 基底クラスから継承 |
| issuer_id | - | No | 基底クラスから継承 |
| new_shares_authorized | [Numeric](../../../types/Numeric.md) | Yes | 新しい発行可能株式数 |
| board_approval_date | [Date](../../../types/Date.md) | No | 取締役会承認日付 |
| stockholder_approval_date | [Date](../../../types/Date.md) | No | 株主承認日付 |