# discordpy-startup

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

- Herokuでdiscord.pyを始めるテンプレートです。
- Use Template からご利用ください。
- 使い方はこちら： [Discord Bot 最速チュートリアル【Python&Heroku&GitHub】 - Qiita](https://qiita.com/1ntegrale9/items/aa4b373e8895273875a8)

## 環境構築
### 依存パッケージインストール
```
poetry install
```

### 環境変数設定
リポジトリ直下に `.env` ファイルを作成し、以下のような内容を記述してください。

```
DISCORD_BOT_TOKEN=取得したトークン
```

## ローカル実行
```
poetry shell
heroku local
```

## デプロイ方法
1. herokuにデプロイ `git push heroku master` 
2. デプロイ先のURL取得 `heroku info -s` など `heroku open` でも可能
3. 対象のgithubレポジトリで settings -> Webhooks -> Add Webhook を選択
4. デプロイ先のURL、送信の形式(JSON)、全てのイベントの通知を設定

## 各種ファイル情報

### discordbot.py
PythonによるDiscordBotのアプリケーションファイルです。

### requirements.txt
使用しているPythonのライブラリ情報の設定ファイルです。

### Procfile
Herokuでのプロセス実行コマンドの設定ファイルです。

### runtime.txt
Herokuでの実行環境の設定ファイルです。

### app.json
Herokuデプロイボタンの設定ファイルです。

### .github/workflows/flake8.yaml
GitHub Actions による自動構文チェックの設定ファイルです。

### .gitignore
Git管理が不要なファイル/ディレクトリの設定ファイルです。

### LICENSE
このリポジトリのコードの権利情報です。MITライセンスの範囲でご自由にご利用ください。

### README.md
このドキュメントです。
