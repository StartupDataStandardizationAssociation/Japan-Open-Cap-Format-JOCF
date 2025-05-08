# Type - Elective Conversion At Will

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/conversion_triggers/ElectiveConversionAtWillTrigger.schema.json`

## Description
投資家の意思で実行されるトリガー

## Composed from
- [ConversionTrigger](../../../primitives/types/conversion_triggers/ConversionTrigger.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | const (ELECTIVE_AT_WILL) | Yes |  |
| nickname | string | No | トリガーのニックネーム |
| trigger_description | string | No | トリガーの説明 |
| trigger_id | unknown | Yes |  |
| conversion_right | unknown | Yes |  |