PostRssBot
====

rssを取得しDiscord上に整形して投稿するBot

## Description
rssの各タイトルと概要をSlack形式に整形しWebhookを利用して投稿する。
crontab等での定期実行を前提としており、自動で前回取得時の日時を保持し多重投稿を防ぐように制御。

## Requirement
$ python3 -m pip install requests requests_oauthlib

$ python3 -m pip install pytz

## Usage
翻訳にGoogleのCloud Translation APIを利用している為、
利用する場合は下記を参考に認証情報を設定する。

[google-cloud authentication](https://google-cloud-python.readthedocs.io/en/latest/core/auth.html#client-provided-authentication)

## Author

[orerus](https://github.com/orerus)

[twitter](https://twitter.com/orerus)