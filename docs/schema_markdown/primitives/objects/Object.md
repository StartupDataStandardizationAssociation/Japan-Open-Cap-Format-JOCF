# Primitive - Object

ID = `https://jocf.startupstandard.org/jocf/main/schema/primitives/objects/Object.schema.json`

## Description
他のすべてのオブジェクトによって拡張される抽象オブジェクト

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| id | string | Yes | オブジェクトの識別子 |
| comments | array of string | No | オブジェクトに関連して保存されている構造化されていないテキストコメント |
| object_type | [ObjectType](../../enums/ObjectType.md) | Yes | Object type field |