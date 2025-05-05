# JOCF 証券保有者ファイル

ID = `https://jocf.startupstandard.org/jocf/main/schema/files/SecurityHoldersFile.schema.json`

## Composed from
- [File](../types/File.schema.json)

## Properties

| PropertyName | Type | Required |
|-------------|------|----------|
| items | 証券保有者のリスト <br> array of [SecurityHolder](../objects/SecurityHolder.schema.json) | Yes |
| file_type | const (JOCF_SECURITY_HOLDERS_FILE) | Yes |