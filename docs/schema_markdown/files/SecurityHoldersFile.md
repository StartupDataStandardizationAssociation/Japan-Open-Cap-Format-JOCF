# JOCF 証券保有者ファイル

ID = `https://jocf.startupstandard.org/jocf/main/schema/files/SecurityHoldersFile.schema.json`

## Composed from
- [File](../types/File.md)

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| items | array of [SecurityHolder](../objects/SecurityHolder.md) | Yes | 証券保有者のリスト |
| file_type | const (JOCF_SECURITY_HOLDERS_FILE) | Yes |  |