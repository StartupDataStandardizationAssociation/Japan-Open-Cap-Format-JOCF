# トランザクション

ID = `https://jocf.startupstandard.org/jocf/main/schema/files/TransactionsFile.schema.json`

## Description
発生したトランザクションを記録するファイル

## Composed from
- [File](../types/File.schema.json)

## Properties

| PropertyName | Type | Required |
|-------------|------|----------|
| items | JOCFトランザクションオブジェクトのリスト <br> one of: <br> - [StockIssuance](../objects/transactions/issuance/StockIssuance.schema.json)<br> - [StockOptionIssuance](../objects/transactions/issuance/StockOptionIssuance.schema.json)<br> - [ConvertibleIssuance](../objects/transactions/issuance/ConvertibleIssuance.schema.json)<br> - [StockConversion](../objects/transactions/conversion/StockConversion.schema.json)<br> - [ConvertibleConversion](../objects/transactions/conversion/ConvertibleConversion.schema.json)<br> - [StockOptionExercise](../objects/transactions/exercise/StockOptionExercise.schema.json)<br> - [StockOptionCancellation](../objects/transactions/cancellation/StockOptionCancellation.schema.json)<br> - [StockTransfer](../objects/transactions/transfer/StockTransfer.schema.json)<br> - [StockSplit](../objects/transactions/split/StockSplit.schema.json)<br> - [StockMerger](../objects/transactions/merger/StockMerger.schema.json)<br> - [SecurityholdersAgreementExecution](../objects/transactions/agreement/SecurityholdersAgreementExecution.schema.json)<br> - [SecurityholdersAgreementModification](../objects/transactions/agreement/SecurityholdersAgreementModification.schema.json)<br> - [SecurityholdersAgreementTermination](../objects/transactions/agreement/SecurityholdersAgreementTermination.schema.json) | Yes |
| file_type | const (JOCF_TRANSACTIONS_FILE) | Yes |