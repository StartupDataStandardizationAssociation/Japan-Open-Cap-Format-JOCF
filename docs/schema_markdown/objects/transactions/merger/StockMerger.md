# 株式併合トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/merger/StockMerger.schema.json`

## Description
株式併合トランザクション

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_MERGER) | No |  |
| id | string | Yes | この株式併合トランザクションのID |
| stock_class_id | string | Yes | 併合する株式種類のID |
| merger_ratio | [Ratio](../../../types/Ratio.md) | Yes | 新株数に対して古い株数の比率 |
| description | string | No | 説明 |
| date | string | Yes | 発生日時 |