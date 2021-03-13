from typing import List, Union, Dict
from discord import Message, Member, User, Reaction, TextChannel
from ..discord_event_handler import DiscordEventHandler, MentionHandler, ReactionAddHandler
from .states import ChannelState, StandByState, ChannelContext

class ChannelsEventHandler(DiscordEventHandler):
    """
    Discord 全体のイベントを受け取り，イベントが発生したチャンネルに紐づく ChannelState にイベントを送信する
    """


    channel_states: Dict[TextChannel, ChannelState]
    """チャンネルに紐づく ChannelState インスタンスたち"""

    def __init__(self):
        super().__init__()
        self.channel_states = {}
        self.mention_handlers = [self.on_mention]
        self.reaction_add_handlers = [self.on_reaction_add]

    async def on_mention(self, message: Message):
        """
        mention イベントを適切なチャンネルに紐づく ChannelState インスタンスのハンドラに渡し，
        ChannelState を更新する
        """
        # TODO: on_reaction_add と共通化する
        channel = message.channel
        if channel in self.channel_states:
            channel_state = self.channel_states[channel]
        else:
            channel_state = StandByState(ChannelContext(channel))
        next_state = await channel_state.on_mention(message)
        if next_state is not None:
            if isinstance(next_state, StandByState):
                # 待機状態
                # 消さないといつまでもメモリに残り続けるので消す
                self.channel_states.pop(channel, None)
            else:
                self.channel_states[channel] = next_state

    async def on_reaction_add(self, reaction: Reaction, user: Union[Member, User]):
        """
        reaction_add イベントを適切なチャンネルに紐づく ChannelState インスタンスのハンドラに渡し，
        ChannelState を更新する
        """
        channel = reaction.message.channel
        if channel in self.channel_states:
            channel_state = self.channel_states[channel]
        else:
            channel_state = StandByState(ChannelContext(channel))
        next_state = await channel_state.on_reaction_add(reaction, user)
        if next_state is not None:
            if isinstance(next_state, StandByState):
                # 待機状態
                # 消さないといつまでもメモリに残り続けるので消す
                self.channel_states.pop(channel, None)
            else:
                self.channel_states[channel] = next_state
