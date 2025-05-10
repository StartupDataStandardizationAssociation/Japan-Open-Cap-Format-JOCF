# ドキュメントの自動生成

本リポジトリでは、スキーマファイル(.schema.json)からmarkdownファイル(.md)を自動生成するスクリプトを用意しています。

プロジェクトのルートディレクトリにて、以下のコマンドを実行してください。

```bash
# 指定なしなら仮想環境.venvで実行される
utils/generate-docs/gen_all_docs.sh 
# 任意の仮想環境を指定可能
utils/generate-docs/gen_all_docs.sh (任意の仮想環境名)
```
