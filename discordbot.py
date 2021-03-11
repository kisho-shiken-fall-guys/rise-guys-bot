import os
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config

from icebreak_bot import client as icebreak
from github_bot import client as github
from github_bot import quart as quart

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.environ["DISCORD_BOT_TOKEN"]
QUART_PORT = int(os.environ.get('PORT', 5000))

config = Config()
config.bind = ['0.0.0.0:'+str(QUART_PORT)]

loop = asyncio.get_event_loop()
loop.create_task(github.start(TOKEN))
loop.create_task(icebreak.start(TOKEN))
loop.create_task(serve(quart,config))
loop.run_forever()
