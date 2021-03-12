# rise-guys-bot

## Setup

1. Discord botの作成

2. Herokuへのデプロイ

3. tokenの設定

~~~
heroku config:set DISCORD_BOT_TOKEN=hogehoge
~~~

4. Discord botをサーバーに招待して、通知してほしいchannelで'/test'と打ち込んでください

5. 出てきたchannel idを以下のように設定

~~~
heroku config:set CHANNEL_ID=hogehoge
~~~

6. GitHubのWebhookにHerokuのURL+'/gh-webhook'を設定

ex. https://hogehoge.herokuapp.com/gh-webhook


7. WebhookのSECRET欄に```ruby -rsecurerandom -e 'puts SecureRandom.hex(20)'```などで生成した乱数を設定

8. 同じ乱数を設定

~~~
heroku config:set SECRET_TOKEN=hogehoge
~~~


## Licenses
[MIT License](./LICENSE)

This software is a modification of [DiscordBotPortalJP/discordpy-startup](https://github.com/DiscordBotPortalJP/discordpy-startup) which is licensed under MIT License.

<details>
  <summary>License</summary>
MIT License

Copyright (c) 2019-2020 Discord Bot Portal JP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
</details>
