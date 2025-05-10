# ストックオプション行使トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/exercise/StockOptionExercise.schema.json`

## Description
ストックオプション行使トランザクション

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_OPTION_EXERCISE) | No |  |
| id | string | Yes | このストックオプション行使トランザクションのID |
| quantity | [Numeric](../../../types/Numeric.md) | Yes | 行使個数 |
| description | string | No | 説明 |
| date | string | Yes | 発生日時 |