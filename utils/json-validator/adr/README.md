# Architecture Decision Records (ADR)

このディレクトリには、JSON Validatorプロジェクトにおける重要なアーキテクチャ決定の記録が含まれています。

## ADR形式について

各ADRファイルは以下の構造に従います：

- **ステータス**: 提案中/承認済み/却下/廃止
- **コンテキスト**: 決定が必要となった背景
- **決定**: 採用した解決策
- **理由**: 決定の根拠と考慮事項
- **影響**: 決定による正負の影響
- **代替案**: 検討したが採用しなかった選択肢

## ADR一覧

| 番号 | タイトル | ステータス | 日付 |
|------|----------|------------|------|
| [ADR-0001](./0001-refresolver-lazy-initialization.md) | RefResolver遅延初期化の採用 | 承認済み | 2025-06-21 |

## 新しいADRの作成

新しいADRを作成する際は：

1. 連番を使用（例：0002-new-decision.md）
2. 上記の形式に従う
3. このREADMEのADR一覧を更新する
4. 関連するコードレビューでADRを参照する

## 参考資料

- [Architecture Decision Records (ADR) について](https://adr.github.io/)
- [ADRベストプラクティス](https://github.com/joelparkerhenderson/architecture-decision-record)