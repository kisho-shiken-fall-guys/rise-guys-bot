"""
雑多な便利関数たち
"""

import re
from discord import Message

def remove_mention(message: Message) -> str:
    """メッセージの内容からメンションを除去した文字列を返す"""
    remove_content = re.sub('<@(.*?)>', '', message.content)
    return remove_content.strip()
