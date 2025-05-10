# ストックオプション発行トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockOptionIssuance.schema.json`

## Description
ストックオプション発行トランザクション

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_OPTION_ISSUANCE) | No |  |
| id | string | Yes | このストックオプション発行トランザクションのID |
| unit_price | [Monetary](../../../types/Monetary.md) | Yes | 1個あたりの払込金額 |
| share_per_unit | [Monetary](../../../types/Monetary.md) | Yes | 1個あたりの付与株式数 |
| quantity | [Numeric](../../../types/Numeric.md) | Yes | 発行個数 |
| description | string | No | 説明 |
| date | string | Yes | 発生日時 |