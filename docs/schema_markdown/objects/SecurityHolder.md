# 証券保有者

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/SecurityHolder.schema.json`

## Composed from
- [Object](../primitives/objects/Object.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (SECURITY_HOLDER) | Yes |  |
| name | [Name](../types/Name.md) | Yes | 証券保有者の名前 |
| id | string | Yes | 証券保有者のID |
| security_holder_type | [SecurityHolderType](../enums/SecurityHolderType.md) | No | 証券保有者の種類 |
| address | string | No | 証券保有者の住所 |
| primary_contact | array of [SecurityHolderPrimaryContact](../types/SecurityHolderPrimaryContact.md) | No | 組織証券保有者の連絡先 |
| contact_info | array of [SecurityHolderContactInfo](../types/SecurityHolderContactInfo.md) | No | 個人証券保有者の連絡先 |