# Type - Automatic Conversion on Condition Trigger

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/conversion_triggers/AutomaticConversionOnConditionTrigger.schema.json`

## Description
条件により自動的に発動するトリガー

## Composed from
- [ConversionTrigger](../../../../primitives/types/conversion_triggers/ConversionTrigger.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | const (AUTOMATIC_ON_CONDITION) | Yes |  |
| trigger_condition | string | Yes | 変換が行われるためにどの条件が満たされなければならないかを説明する法的な文言 |
| trigger_description | string | No | トリガーの説明 |
| nickname | string | No | トリガーのニックネーム |
| trigger_id | unknown | Yes |  |
| conversion_right | unknown | Yes |  |