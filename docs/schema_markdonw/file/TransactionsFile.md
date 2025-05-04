# トランザクション

## Description
発生したトランザクションを記録するファイル

## Properties

| PropertyName | Type | Required |
|-------------|------|----------|
| items | array of: | Yes |
|  | - StockIssuance |  |
|  | - StockOptionIssuance |  |
|  | - ConvertibleIssuance |  |
|  | - StockConversion |  |
|  | - ConvertibleConversion |  |
|  | - StockOptionExercise |  |
|  | - StockOptionCancellation |  |
|  | - StockTransfer |  |
|  | - StockSplit |  |
|  | - StockMerger |  |
|  | - SecurityholdersAgreementExecution |  |
|  | - SecurityholdersAgreementModification |  |
|  | - SecurityholdersAgreementTermination |  |
|  | JOCFトランザクションオブジェクトのリスト |  |
| file_type | const (JOCF_TRANSACTIONS_FILE) | Yes |