# ストックオプション消却トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/cancellation/StockOptionCancellation.schema.json`

## Description
ストックオプション消却トランザクション

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_OPTION_CANCELLATION) | No |  |
| id | string | Yes | このストックオプション消却トランザクションのID |
| quantity | [Numeric](../../../types/Numeric.md) | Yes | 消却個数 |
| description | string | No | 説明 |
| date | string | Yes | ストックオプション消却トランザクションの発生日時 |