"""
基本的なクラスの定義
"""

import abc
from typing import Union, Optional
from discord import Message, Member, User, Reaction, TextChannel

class ChannelContext():
    """
    1 つのチャンネルが持つ状態のうち，ChannelState のどの派生クラスでも同じ値を持つ情報

    Attributes
    ----------
    channel
        ChannelState に紐づくチャンネル
    """
    channel: TextChannel

    def __init__(
        self,
        channel: TextChannel,
    ):
        self.channel = channel

class ChannelState(abc.ABC):
    """
    ある 1 つのチャンネルの現在の状態を表す
    チャンネルでイベントが発生した場合に，返答等を行った後，次の状態を出力する
    """

    context: ChannelContext

    def __init__(self, context: ChannelContext):
        self.context = context

    async def on_mention(self, message: Message) -> Optional['ChannelState']:
        """
        mention イベントを受け取って，必要な処理を行い，次の状態を返す
        ただし None を返してもよく，これは「現在の状態の維持」を意味する
        """
        return None

    async def on_reaction_add(self, reaction: Reaction, user: Union[Member, User]) -> Optional['ChannelState']:
        """
        reaction_add イベントを受け取って，必要な処理を行い，次の状態を返す
        ただし None を返してもよく，これは「現在の状態の維持」を意味する
        """
        return None
