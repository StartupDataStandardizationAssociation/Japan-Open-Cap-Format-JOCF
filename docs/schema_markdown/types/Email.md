# Type - Email

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/Email.schema.json`

## Description
Eメールアドレスとその種類

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| email_type | [EmailType](../../enums/EmailType.md) | Yes | Eメールアドレスの種類(e.g. 個人用、ビジネス用) |
| email_address | string | Yes | Eメールアドレス |