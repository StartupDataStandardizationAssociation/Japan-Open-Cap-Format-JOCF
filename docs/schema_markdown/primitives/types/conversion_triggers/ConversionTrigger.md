# Primitive - Conversion Trigger Type

ID = `https://jocf.startupstandard.org/jocf/main/schema/primitives/types/conversion_triggers/ConversionTrigger.schema.json`

## Description
転換トリガーに関する基底クラス

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | [ConversionTriggerType](../../../enums/ConversionTriggerType.md) | Yes | 転換トリガーの種別 |
| trigger_id | string | Yes | トリガーのID |
| conversion_right | unknown | Yes | トリガー条件を満たした場合に発動する転換権 |