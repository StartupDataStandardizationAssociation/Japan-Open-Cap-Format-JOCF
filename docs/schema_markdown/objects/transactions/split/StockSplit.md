# 株式分割トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/split/StockSplit.schema.json`

## Description
株式分割トランザクション

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_SPLIT) | No |  |
| id | string | Yes | この株式分割トランザクション |
| stock_class_id | string | Yes | この株式分割トランザクションで分割される株式種類のID |
| split_ratio | [Ratio](../../../types/Ratio.md) | Yes | 古い株数に対して新株数の比率 |
| description | string | No | 説明 |
| date | string | Yes | 発生日時 |