---
name: generate-env
description: パイプラインの組み合わせに応じた .env.local テンプレートを生成する。例: "kintone to Snowflake"
argument-hint: "[source] to [destination]"
allowed-tools: Bash, Read, Glob
---

# Generate Env Skill

ユーザーが指定したソース/デスティネーションの組み合わせに必要な環境変数のみを含む `.env.local` テンプレートを自動生成する。

## 入力パース

ユーザー入力: `$ARGUMENTS`

以下を解析:
1. **ソース（転送元）**: "to" の前の部分（例: "kintone", "google spreadsheets"）
2. **デスティネーション（転送先）**: "to" の後の部分（例: "Snowflake", "BigQuery"）

ソース名を正規化（スペースはアンダースコアに、小文字化）:
- "kintone" → `kintone`
- "google spreadsheets" / "Google Spreadsheets" → `google_spreadsheets`

デスティネーション名を正規化:
- "BigQuery" / "bigquery" → `bigquery`
- "Snowflake" / "snowflake" → `snowflake`

## 実行フロー

### 1. コネクタ対応確認

`reference/connector-catalog.md` をReadで読み込み、指定されたソース/デスティネーションが対応しているか確認する。
未対応の場合は「未対応のコネクタです」と案内して停止。

### 2. .env.local 存在確認

```bash
[ -f .env.local ] && echo "EXISTS" || echo "NOT_FOUND"
```

### 3. テンプレート生成

- `.env.local` が **存在しない** 場合:
  ```bash
  python3 .claude/skills/infrastructure/generate-env/generate_env_template.py --source {src} --destination {dest}
  ```

- `.env.local` が **存在する** 場合:
  - ユーザーに上書きの確認を取る
  - 承認された場合: `--force` オプションで実行（バックアップが自動作成される）
    ```bash
    python3 .claude/skills/infrastructure/generate-env/generate_env_template.py --source {src} --destination {dest} --force
    ```
  - 拒否された場合: 停止

### 4. 結果表示と案内

生成されたテンプレートの内容を表示し、以下を案内:

1. `.env.local` の各変数に適切な値を設定してください
2. モードA/Bの説明:
   - **モードA（既存接続）**: TROCCO管理画面で接続を事前に作成し、そのIDを設定（推奨）
   - **モードB（Terraform新規作成）**: 接続IDを空にし、認証情報を直接設定
3. 設定完了後、`/setup-pipeline {src} to {dest}` でパイプライン構築を実行できます
