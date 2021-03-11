# インストールした discord.py を読み込む
import discord
from discord import Message, Member, User, Reaction
import re
from typing import List, Union, NamedTuple, Optional
import asyncio
from emoji import emojize
from .handlers import handlers

# 接続に必要なオブジェクトを生成
client = discord.Client()
# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')



# メッセージ受信時に動作する処理
@client.event
async def on_message(message: Message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    if client.user in message.mentions: # 話しかけられたかの判定
        await asyncio.gather(*[handler(message) for handler in handlers.on_mention])

@client.event
async def on_reaction_add(reaction: Reaction, user: Union[Member, User]):
    if user.bot:
        return
    await asyncio.gather(*[handler(reaction, user) for handler in handlers.on_reaction_add])
