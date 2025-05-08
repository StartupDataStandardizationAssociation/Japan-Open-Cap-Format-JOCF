# トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json`

## Description
発生したトランザクションを記録するファイル

## Composed from
- [File](../types/File.md)

## Properties

| PropertyName | Type | Required |
|-------------|------|----------|
| items | JOCFトランザクションオブジェクトのリスト <br> one of: <br> - [StockIssuance](../objects/transactions/issuance/StockIssuance.md)<br> - [StockOptionIssuance](../objects/transactions/issuance/StockOptionIssuance.md)<br> - [ConvertibleIssuance](../objects/transactions/issuance/ConvertibleIssuance.md)<br> - [StockConversion](../objects/transactions/conversion/StockConversion.md)<br> - [ConvertibleConversion](../objects/transactions/conversion/ConvertibleConversion.md)<br> - [StockOptionExercise](../objects/transactions/exercise/StockOptionExercise.md)<br> - [StockOptionCancellation](../objects/transactions/cancellation/StockOptionCancellation.md)<br> - [StockTransfer](../objects/transactions/transfer/StockTransfer.md)<br> - [StockSplit](../objects/transactions/split/StockSplit.md)<br> - [StockMerger](../objects/transactions/merger/StockMerger.md)<br> - [SecurityholdersAgreementExecution](../objects/transactions/agreement/SecurityholdersAgreementExecution.md)<br> - [SecurityholdersAgreementModification](../objects/transactions/agreement/SecurityholdersAgreementModification.md)<br> - [SecurityholdersAgreementTermination](../objects/transactions/agreement/SecurityholdersAgreementTermination.md) | Yes |
| file_type | const (JOCF_TRANSACTIONS_FILE) | Yes |