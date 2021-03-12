"""
1 つのチャンネルがとりうる状態と遷移
"""

import re
from typing import List, Union, NamedTuple, Optional, Callable, Awaitable, TypeVar, Sequence, Tuple, Iterable
from discord import Message, Member, User, Reaction, TextChannel
from ...client import client
from ...utils import remove_mention
from ...db import Genre, Odai, PollCandidate
from ..base import ChannelState, ChannelContext
from .selection import SelectionState, send_selection_message
from .poll import PollResultItem, PollStateBase, send_poll_message, format_poll_result


class StandByState(ChannelState):
    """
    待機状態
    """

    async def on_mention(self, message: Message) -> Optional[ChannelState]:
        text = remove_mention(message)
        if re.match('^(お題ください|genre)$', text):
            return await GenreSelectionState.create(self.context)
        if re.match('^(お題追加|genre add)$', text):
            return await GenreSelectionForAddState.create(self.context)
        return None


class GenreSelectionState(SelectionState[Genre]):
    """
    ジャンル選択待ち状態
    """

    @staticmethod
    async def create(context: ChannelContext) -> 'GenreSelectionState':
        """
        ジャンル選択メッセージを送信し，GenreSelectionState インスタンスを返す

        Parameters
        ----------
        context
            送信先チャンネルの ChannelContext
        """

        candidates = list(Genre.query_all())
        message = await send_selection_message(context.channel, candidates, comment_top="興味のあるカテゴリにリアクションを押してください！")
        return GenreSelectionState(context, candidates, message)

    async def on_selection(self, genre: Genre) -> Optional[ChannelState]:
        return await OdaiSelectionState.create(self.context, genre)


class OdaiSelectionState(SelectionState[Odai]):
    """
    お題選択待ち状態
    """

    @staticmethod
    async def create(context: ChannelContext, genre: Genre) -> 'OdaiSelectionState':
        """
        お題選択メッセージを送信し，OdaiSelectionState インスタンスを返す

        Parameters
        ----------
        context
            送信先チャンネルの ChannelContext
        genre
            ジャンル
        """

        candidates = list(Odai.query(genre))
        if len(candidates) == 0:
            raise Exception(f'Genre {genre.genre_id} does not have odai')
        message = await send_selection_message(context.channel, candidates, comment_top="興味のある話題のリアクションを押してください！")
        return OdaiSelectionState(context, candidates, message)

    async def on_selection(self, odai: Odai) -> Optional[ChannelState]:
        return await PollState.create(self.context, odai)


class PollState(PollStateBase):
    """
    投票中状態
    """

    @staticmethod
    async def create(context: ChannelContext, odai: Odai) -> 'PollState':
        """
        投票メッセージを送信し，PollState インスタンスを返す

        Parameters
        ----------
        context
            送信先チャンネルの ChannelContext
        odai
            お題
        """

        candidates = list(PollCandidate.query(odai))
        if len(candidates) == 0:
            raise Exception(f'Odai {odai.odai_id} does not have any poll candidates')
        message = await send_poll_message(context.channel, candidates, comment_top="選択肢です！！複数投票可能だよー！！")
        return PollState(context, candidates, message)

    async def on_close(self, result: Iterable[PollResultItem]) -> Optional[ChannelState]:
        await self.message.channel.send(format_poll_result(result))
        return StandByState(self.context)


class GenreSelectionForAddState(SelectionState[Genre]):
    """
    投票選択肢追加における，ジャンル選択待ち状態
    """

    @staticmethod
    async def create(context: ChannelContext) -> 'GenreSelectionForAddState':
        """
        お題選択メッセージを送信し，OdaiSelectionForAddState インスタンスを返す

        Parameters
        ----------
        context
            送信先チャンネルの ChannelContext
        """

        candidates = list(Genre.query_all())
        message = await send_selection_message(context.channel, candidates, comment_top="選択肢を追加したい話題のカテゴリにリアクションを押してください！")
        return GenreSelectionForAddState(context, candidates, message)

    async def on_selection(self, genre: Genre) -> Optional[ChannelState]:
        return await OdaiSelectionForAddState.create(self.context, genre)


class OdaiSelectionForAddState(SelectionState[Odai]):
    """
    投票選択肢追加における，お題選択待ち状態
    """

    @staticmethod
    async def create(context: ChannelContext, genre: Genre) -> 'OdaiSelectionForAddState':
        """
        お題選択メッセージを送信し，OdaiSelectionForAddState インスタンスを返す

        Parameters
        ----------
        context
            送信先チャンネルの ChannelContext
        genre
            ジャンル
        """

        candidates = list(Odai.query(genre))
        if len(candidates) == 0:
            raise Exception(f'Genre {genre.genre_id} does not have odai')
        message = await send_selection_message(context.channel, candidates, comment_top="選択肢を追加したい話題のリアクションを押してください！")
        return OdaiSelectionForAddState(context, candidates, message)

    async def on_selection(self, odai: Odai) -> Optional[ChannelState]:
        return await AddPollCandidateState.create(self.context, odai)


class AddPollCandidateState(ChannelState):
    """
    投票選択肢追加における，追加する選択肢入力待ち状態
    """

    odai: Odai

    def __init__(
        self,
        context: ChannelContext,
        odai: Odai
    ) -> None:
        super().__init__(context)
        self.odai = odai

    @staticmethod
    async def create(context: ChannelContext, odai: Odai) -> 'AddPollCandidateState':
        """
        お題選択メッセージを送信し，AddPollCandidateState インスタンスを返す

        Parameters
        ----------
        context
            送信先チャンネルの ChannelContext
        odai
            お題
        """

        await context.channel.send(f'追加する選択肢を「{client.user.mention} hogehoge」のように入力してください。')
        return AddPollCandidateState(context, odai)

    async def on_mention(self, message: Message) -> Optional[ChannelState]:
        candidate_name = remove_mention(message)
        if candidate_name:
            PollCandidate.add(self.odai, candidate_name)
            await self.context.channel.send(f'{candidate_name} を追記しました。')
            return StandByState(self.context)
        return None
