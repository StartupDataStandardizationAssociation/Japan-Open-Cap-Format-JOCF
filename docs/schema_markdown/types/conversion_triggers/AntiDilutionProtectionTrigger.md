# Type - Conversion on Down Round Trigger

ID = `https://jocf.startupstandard.org/jocf/main/schema/types/conversion_triggers/AntiDilutionProtectionTrigger.schema.json`

## Description
ダウンラウンドによる希薄化防止条項が発動するトリガー

## Composed from
- [ConversionTrigger](../../../../primitives/types/conversion_triggers/ConversionTrigger.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| type | const (ANTI_DILUTION_PROTECTION) | Yes |  |
| nickname | string | No | トリガーのニックネーム |
| trigger_condition | string | No | 希薄化防止が発動可能となる条件を説明する法的な文言 |
| non_triggering_condition | string | No | 希薄化防止が発動可能となる条件を満たした上で、希薄化防止による転換を実施しない条件を説明する法的な文言 |
| anti_dilution_protection_type | string | Yes | 希薄化防止種別 |
| incentive_exclusion_ratio | [Numeric](../../types/Numeric.md) | No | 希薄化防止対象から除外される従業員インセンティブの比率 |
| trigger_id | unknown | Yes |  |
| trigger_description | unknown | No |  |
| conversion_right | unknown | Yes |  |