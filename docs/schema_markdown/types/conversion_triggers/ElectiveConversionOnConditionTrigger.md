# Type - Elective Conversion On Condition

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/conversion_triggers/ElectiveConversionOnConditionTrigger.schema.json`

## Description
特定の条件を満たした場合に転換するかどうかを選択可能なトリガー

## Composed from
- [ConversionTrigger](../../primitives/types/conversion_triggers/ConversionTrigger.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | const (ELECTIVE_ON_CONDITION) | Yes |  |
| trigger_condition | string | Yes | 転換を選択可能となる条件を表す法的文言 |
| trigger_id | unknown | Yes |  |
| nickname | unknown | No |  |
| trigger_description | unknown | No |  |
| conversion_right | unknown | Yes |  |