# JOCF Securityholders Agreement File

ID = `https://jocf.startupstandard.org/jocf/main/schema/files/SecurityHoldersAgreementFile.schema.json`

## Description
証券保有者間同意に関するファイル

## Composed from
- [File](../types/File.md)

## Properties

| PropertyName | Type | Required |
|-------------|------|----------|
| items | 証券保有者間同意の一覧 <br> one of: <br> - [MasterSecurityholdersAgreement](../objects/MasterSecurityholdersAgreement.md)<br> - [AcquisitionDistributionAgreement](../objects/AcquisitionDistributionAgreement.md) | Yes |
| file_type | const (JOCF_SECURITYHOLDERS_AGREEMENT_FILE) | Yes |