# 株式発行トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/transactions/issuance/StockIssuance.schema.json`

## Description
株式発行トランザクション

## Composed from
- [Object](../../../primitives/objects/Object.md)
- [Transaction](../../../primitives/objects/transactions/Transaction.md)
- [Issuance](../../../primitives/objects/transactions/issuance/Issuance.md)
- [SecurityTransaction](../../../primitives/objects/transactions/SecurityTransaction.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (TX_STOCK_ISSUANCE) | Yes |  |
| id | string | Yes | この株式発行トランザクションのID |
| stock_class_id | string | Yes | この株式発行で発行する株式種類のID |
| securityholder_id | string | Yes | 発行する株式を受け取る証券保有者のID |
| share_price | [Monetary](../../../types/Monetary.md) | Yes | 1株の価格 |
| quantity | [Numeric](../../../types/Numeric.md) | Yes | 引受株式数 |
| description | string | No | 説明 |
| date | string | Yes | 契約締結日 |
| payment_due_date | string | No | 払込期日 |
| series_name | string | No | シリーズ名 |
| representations_and_warranties_by_issuing_company | [IssuerRepresentationsAndWarranties](../../../primitives/types/IssuerRepresentationsAndWarranties.md) | No | 発行会社による表明および保証 |
| representations_and_warranties_by_investor | [IssuerRepresentationsAndWarranties](../../../primitives/types/IssuerRepresentationsAndWarranties.md) | No | 投資家による表明および保証 |
| security_id | - | Yes | 基底クラスから継承 |