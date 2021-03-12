"""
リアクション選択における共通処理たち
"""

import abc
import textwrap
from typing import Union, Generic, TypeVar, Sequence, Optional
from discord import Message, Member, User, Reaction, TextChannel
from ...emojis import number_emojis
from ..base import ChannelState, ChannelContext

Value = TypeVar('Value')

class SelectionState(ChannelState, abc.ABC, Generic[Value]):
    """
    リアクション選択を待つ状態

    実際に選択が行われた際の処理を抽象メソッド on_selection に実装することが必要

    Attributes
    ----------
    candidates
        選択肢のリスト
    message
        選択肢一覧が表示されている投稿
    """

    candidates: Sequence[Value]
    message: Message

    def __init__(
        self,
        context: ChannelContext,
        candidates: Sequence[Value],
        message: Message,
    ) -> None:
        super().__init__(context)
        self.candidates = candidates
        self.message = message

    @abc.abstractmethod
    async def on_selection(self, value: Value) -> Optional[ChannelState]:
        """
        選択が行われた際に呼び出される
        次に遷移する状態を返す

        Parameters
        ----------
        value
            選択された選択肢 (candidates の要素)
        """
        raise NotImplementedError

    async def on_reaction_add(self, reaction: Reaction, user: Union[Member, User]) -> Optional[ChannelState]:
        """
        reaction_add イベントを受け取り，選択肢に対するリアクションであれば on_selection を呼び出して選択の終了を伝える
        """
        if reaction.message == self.message:
            # 選択肢メッセージへのリアクション
            if reaction.emoji in number_emojis:
                index = number_emojis.index(reaction.emoji)
                if index < len(self.candidates):
                    selected = self.candidates[index]
                    return await self.on_selection(selected)
        return None

async def send_selection_message(channel: TextChannel, candidates: Sequence[Value], comment_top="", comment_bottom="") -> Message:
    """
    選択肢一覧メッセージを送信する

    Parameters
    ----------
    channel
        送信先チャンネル
    candidates
        選択肢のリスト
    comment_top
        メッセージ上部に記載する文字列
    comment_bottom
        メッセージ下部に記載する文字列
    """

    if len(candidates) > len(number_emojis):
        raise Exception(f'cannot handle more than {len(number_emojis)} candidates')

    used_emojis = number_emojis[:len(candidates)]

    candidates_text = '\n'.join(f'{emoji} {candidate}' for candidate, emoji in zip(candidates, used_emojis))
    text = textwrap.dedent("""
        {}

        {}

        {}
    """).format(comment_top, candidates_text, comment_bottom)
    reply: Message = await channel.send(text)

    for emoji in used_emojis:
        await reply.add_reaction(emoji) # TODO: 並列化
    
    return reply
