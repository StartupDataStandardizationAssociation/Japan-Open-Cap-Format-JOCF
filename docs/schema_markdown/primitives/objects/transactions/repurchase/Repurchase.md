# Primitive - Security Repurchase Transaction

ID = `https://jocf.startupstandard.org/jocf/main/schema/primitives/objects/transactions/repurchase/Repurchase.schema.json`

## Description
証券の買い戻し(e.g. 自社株買い)トランザクションの基底クラス

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| price | [Monetary](../../../../types/Monetary.md) | Yes | 証券1単位当たりの買い戻し価格 |
| quantity | [Numeric](../../../../types/Numeric.md) | Yes | 買い戻し数量 |
| consideration_text | string | No | 証券の買戻しに伴って発生する考慮事項 |
| balance_security_id | string | No | 部分的な買い戻しの場合に、買い戻し後の残りの残高を示すID |