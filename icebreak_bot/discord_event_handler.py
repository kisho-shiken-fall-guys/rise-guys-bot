import asyncio
from typing import List, Union, Callable, Awaitable
from discord import Message, Member, User, Reaction

MentionHandler = Callable[[Message], Awaitable[None]]
ReactionAddHandler = Callable[[Reaction, Union[Member, User]], Awaitable[None]]

class DiscordEventHandler():
    """
    Discord のイベントリスナー
    同一イベントに複数のイベントハンドラを割り当てられる点で，discord.py より少し便利

    Attributes
    ----------
    mention_handlers
        mention イベントを受け取るハンドラ関数のリスト
    reaction_add_handlers
        reaction_add イベントを受け取るハンドラ関数のリスト
    """

    mention_handlers: List[MentionHandler]

    reaction_add_handlers: List[ReactionAddHandler]

    def __init__(
        self
    ):
        if not (hasattr(type(self), 'mention_handlers') and isinstance(type(self).mention_handlers, property)):
            self.mention_handlers = []
        if not (hasattr(type(self), 'reaction_add_handlers') and isinstance(type(self).reaction_add_handlers, property)):
            self.reaction_add_handlers = []

    async def handle_mention(self, message: Message):
        """
        mention イベントのハンドラ関数たちを並列に実行する
        """

        await asyncio.gather(*[func(message) for func in self.mention_handlers])

    async def handle_reaction_add(self, reaction: Reaction, user: Union[Member, User]):
        """
        reaction_add イベントのハンドラ関数たちを並列に実行する
        """
        await asyncio.gather(*[func(reaction, user) for func in self.reaction_add_handlers])
