# Primitive - Security Transfer Transaction

ID = `https://jocf.startupstandard.org/jocf/main/schema/primitives/objects/transactions/transfer/Transfer.schema.json`

## Description
証券の所有権移転や売買を表現するトランザクションの基底クラス

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| consideration_text | string | No | 証券の移転と共に発生する考慮事項 |
| balance_security_id | string | No | 部分的な移転の場合に、移転後の残りの残高を示すID |
| resulting_security_ids | array of string | Yes | 移転により新しく発生した残高のID一覧 |