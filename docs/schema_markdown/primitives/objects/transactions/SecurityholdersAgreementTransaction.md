# Primitive - Securityholders Agreement Transaction

ID = `https://jocf.startupstandard.org/jocf/main/schema/primitives/objects/transactions/SecurityholdersAgreementTransaction.schema.json`

## Description
証券保有者間同意に影響を与えるすべてのトランザクションオブジェクトによって拡張される抽象トランザクションオブジェクト

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| securityholders_agreement | one of: <br> - [MasterSecurityholdersAgreement](../../../objects/MasterSecurityholdersAgreement.md)<br> - [AcquisitionDistributionAgreement](../../../objects/AcquisitionDistributionAgreement.md) | No | トランザクションの対象である証券保有者間同意 |
| securityholders_agreement_id | string | No | トランザクションの対象である証券保有者間同意の識別子 |