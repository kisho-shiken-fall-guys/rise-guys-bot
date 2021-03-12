"""
投票における共通処理
"""

import abc
import asyncio
import textwrap
from typing import List, Union, Optional, Generic, TypeVar, Sequence, Iterable
from discord import Message, Member, User, Reaction, TextChannel
from emoji import emojize
from ...emojis import number_emojis
from ..base import ChannelState, ChannelContext

Value = TypeVar('Value')

poll_close_emoji = emojize(":white_check_mark:", True)

class PollResultItem(Generic[Value]):
    """
    投票の結果の要素

    Attributes
    ----------
    index
        選択肢一覧における candidate の添字
    candidate
        選択肢
    users
        candidate に投票したユーザーのリスト
    """

    index: int
    candidate: Value
    users: List[Union[Member, User]]

    def __init__(self, index, candidate, users):
        self.index = index
        self.candidate = candidate
        self.users = users


class PollStateBase(ChannelState, abc.ABC, Generic[Value]):
    """
    投票中であり，投票完了を待つ状態

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
    async def on_close(self, result: Iterable[PollResultItem]) -> Optional[ChannelState]:
        """
        投票が終了した際に呼び出される
        次に遷移する状態を返す

        Parameters
        ----------
        result
            投票結果
        """
        raise NotImplementedError

    async def on_reaction_add(self, reaction: Reaction, user: Union[Member, User]) -> Optional[ChannelState]:
        """
        reaction_add イベントを受け取り，投票終了リアクションであれば on_close を呼び出して投票の終了を伝える
        """
        if reaction.message.id != self.message.id:
            return None
        if reaction.emoji != poll_close_emoji:
            return None

        message: Message = reaction.message
        result = await calculate_poll_result(message.reactions, self.candidates)
        return await self.on_close(result)

async def create_poll_result_item(reaction: Reaction, candidates: Sequence[Value]) -> Optional[PollResultItem]:
    """
    1 つの絵文字に対応する選択肢について，PollResultItem インスタンスを作成する

    Parameters
    ----------
    reaction
        リアクション
    candidates
        投票の選択肢一覧
    """
    if reaction.emoji in number_emojis:
        index = number_emojis.index(reaction.emoji)
        if index < len(candidates):
            users = [user for user in await reaction.users().flatten() if not user.bot]
            return PollResultItem(
                index=index,
                candidate=candidates[index],
                users=users,
            )
    return None # 選択肢とは関係ないリアクション

async def calculate_poll_result(reactions: List[Reaction], candidates: Sequence[Value]) -> Iterable[PollResultItem]:
    """
    リアクション一覧から投票結果を計算する

    Parameters
    ----------
    reactions
        リアクションのリスト
    candidates
        投票の選択肢一覧
    """
    items: Iterable[PollResultItem] = filter(
        lambda item: item is not None,
        await asyncio.gather(*[
            create_poll_result_item(reaction, candidates) for reaction in reactions
        ])
    )

    return sorted(items, key=lambda item: item.index)

def format_poll_result(result: Iterable[PollResultItem]) -> str:
    """
    投票結果を文字列に整形する

    Parameters
    ----------
    result
        投票結果
    """
    result_text = '\n'.join([f'{item.candidate} {" ".join([user.mention for user in item.users])}' for item in result])

    return textwrap.dedent("""
        {0}{0}結果発表{0}{0}

        {1}
    """).format(
        emojize(":tada:", True),
        result_text,
    )

async def send_poll_message(channel: TextChannel, candidates: Sequence[Value], comment_top="", comment_bottom="") -> Message:
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

    text = textwrap.dedent("""
        {}

        {}

        {} を押すと集計結果を発表します！
        {}
    """).format(
        comment_top,
        '\n'.join(f'{emoji} {candidate}' for candidate, emoji in zip(candidates, used_emojis)),
        poll_close_emoji,
        comment_bottom,
    )
    reply: Message = await channel.send(text)

    for emoji in used_emojis:
        await reply.add_reaction(emoji) # TODO: 並列化
    await reply.add_reaction(poll_close_emoji)

    return reply
