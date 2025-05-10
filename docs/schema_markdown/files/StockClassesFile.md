# JOCF Stock Classes File

ID = `https://jocf.startupstandard.org/jocf/main/schema/files/StockClassesFile.schema.json`

## Description
株式種類に関するファイル

## Composed from
- [File](../types/File.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| items | one of: <br> - [StockClass](../objects/StockClass.md) | Yes | 株式種類のリスト |
| file_type | const (JOCF_STOCK_CLASSES_FILE) | Yes |  |