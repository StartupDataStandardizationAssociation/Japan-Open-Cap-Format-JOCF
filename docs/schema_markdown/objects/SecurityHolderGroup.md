# Object - Security Holder Group

ID = `https://jocf.startupstandard.org/jocf/main/schema/objects/SecurityHolderGroup.schema.json`

## Description
証券保有者グループ

## Composed from
- [Object](../primitives/objects/Object.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| object_type | const (SECURITYHOLDER_GROUP) | Yes |  |
| name | string | No | 証券保有者グループの名前 |
| securityholder_group_members | array | Yes | 証券保有者グループに属するメンバー |
| id | - | Yes | Objectから継承 |