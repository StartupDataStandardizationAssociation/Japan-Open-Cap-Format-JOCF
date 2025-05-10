# Type - 主要連絡先

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/SecurityHolderPrimaryContact.schema.json`

## Description
法人の投資家の連絡先

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| name | [Name](../types/Name.md) | Yes | 担当者名 |
| phone_numbers | array of [Phone](../types/Phone.md) | No | 担当者の電話番号 |
| emails | array of [Email](../types/Email.md) | No | 担当者のメールアドレス |