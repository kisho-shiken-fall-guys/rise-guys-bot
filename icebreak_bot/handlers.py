import discord
from discord import Message, Member, User, Reaction, TextChannel
import asyncio
import re
from typing import List, Union, NamedTuple, Optional, Callable, Awaitable
import textwrap
from emoji import emojize

class SelectionState(NamedTuple):
    candidates: List[str]
    message: Message

selection_state: Optional[SelectionState] = None

number_emoji_names = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
number_emojis = [emojize(f":{emoji}:", use_aliases=True) for emoji in number_emoji_names]

async def send_selection_message(channel, candidates: List[str]):
    global selection_state

    if (len(candidates) > len(number_emojis)):
        raise Exception(f'cannot handle more than {len(number_emojis)} candidates')

    used_emojis = number_emojis[:len(candidates)]

    text = '\n'.join(f'{emoji} {candidate}' for candidate, emoji in zip(candidates, used_emojis))
    reply: Message = await channel.send(text)
    selection_state = SelectionState(candidates=candidates, message=reply)

    for emoji in used_emojis:
        await reply.add_reaction(emoji) # TODO: 並列化

def remove_mention(message):
    remove_content = re.sub('<@(.*?)>', '', message.content)
    return remove_content.strip()

async def reply_to_odai_request_add(message: Message):
    text = remove_mention(message)
    if re.match('お題ください', text) or re.match('お題追加',text):
        if re.match('お題ください', text):
            describe = "興味のあるカテゴリにリアクションを押してください！\nその後で再度メンションして'select'と送信してください！"
        elif re.match('お題追加',text):
            describe = "説明"
        await message.channel.send(describe)
        path = './icebreak_bot/Genre.txt'
        await read_file_select_common(message, path)

index = -1
async def respond_to_selection_reaction(reaction: Reaction, user: Union[Member, User]):
    global index
    if selection_state is not None and reaction.message.id == selection_state.message.id:
        # 選択肢メッセージへのリアクション
        if reaction.emoji in number_emojis:
            index = number_emojis.index(reaction.emoji)
            if index < len(selection_state.candidates):
                selected = selection_state.candidates[index]
                await reaction.message.channel.send(f'you choose {selected}!')

flag = -1
async def reply_select_to_select_request(message:Message):
    global index
    global flag
    text = remove_mention(message)
    if re.match('select', text):
        describe = "興味のある話題のリアクションを押してください！\nその後で再度メンションして'poll'と送信してください！"
        await message.channel.send(describe)
        if index == 0:
            flag = 0
            path = './icebreak_bot/select/chat.txt'
        elif index == 1:
            flag = 1
            path = './icebreak_bot/select/religious_war.txt'
        elif index == 2:
            flag = 2
            path = './icebreak_bot/select/technology.txt'
        await read_file_select_common(message,path)

async def read_file_select_common(message, path):
    global index
    index = -1
    file = open(path, 'r', encoding='utf_8_sig')
    candidates = file.readlines()
    file.close()
    await send_selection_message(message.channel, candidates)


class PollState(NamedTuple):
    candidates: List[str]
    message: Message

poll_state: Optional[PollState] = None

add_flag = False
async def reply_to_poll_request_add(message: Message):
    global index
    global flag
    global add_flag
    '''
    本来はユーザーがお題を選択するとbotが投票を送信するが、そこの機能が実装できていないので
    「<メンション> poll」と言われたらbotが投票メッセージを送信する

    上述の機能が実装できたらこの関数は不要
    '''
    text = remove_mention(message)
    text2 = text.replace('add ', '')
    if re.match('poll', text) or re.match('add', text):
        if re.match('poll', text):
            describe = "選択肢です！！複数投票可能だよー！！"
        elif re.match('add', text):
            describe = "説明"
            add_flag = True
        await message.channel.send(describe)
        if flag == 0:
            if index == 0:
                path = './icebreak_bot/poll/hobby.txt'
            elif index == 1:
                path = './icebreak_bot/poll/happiness_recent.txt'
            elif index == 2:
                path = './icebreak_bot/poll/sad_recent.txt'
            elif index == 3:
                path = './icebreak_bot/poll/like_food.txt'
            elif index == 4:
                path = './icebreak_bot/poll/live_in.txt'
        elif flag == 1:
            if index == 0:
                path = './icebreak_bot/poll/editor.txt'
            elif index == 1:
                path = './icebreak_bot/poll/tab_or_space.txt'
            elif index == 2:
                path = './icebreak_bot/poll/use_browser.txt'
            elif index == 3:
                path = './icebreak_bot/poll/Linux_distribution.txt'
            elif index == 4:
                path = './icebreak_bot/poll/zero_trouble.txt'
            elif index == 5:
                path = './icebreak_bot/poll/like_os.txt'
        elif flag == 2:
            if index == 0:
                path = './icebreak_bot/poll/like_programming_language.txt'
            elif index == 1:
                path = './icebreak_bot/poll/interesting_lecture.txt'
            elif index == 2:
                path = './icebreak_bot/poll/from_course.txt'
        await read_write_file_poll_common(message,path,text2)

async def read_write_file_poll_common(message:Message, path, postscript_str):
    global flag
    global index
    global add_flag
    flag = -1
    index = -1
    if add_flag:
        add_flag = False
        file = open(path, 'a', encoding='utf_8_sig')
        file.write('\n'+ postscript_str)
        file.close
        text = postscript_str + "を追記しました"
        await message.channel.send(text)
        await read_file_select_common(message.channel, path)
    else:
        file = open(path, 'r', encoding='utf_8_sig')
        candidates = file.readlines()
        file.close()
        await send_poll_message(message.channel,candidates)

poll_close_emoji = emojize(":white_check_mark:", True)

async def send_poll_message(channel: TextChannel, candidates: List[str]):
    global poll_state

    if (len(candidates) > len(number_emojis)):
        raise Exception(f'cannot handle more than {len(number_emojis)} candidates')

    used_emojis = number_emojis[:len(candidates)]

    text = textwrap.dedent("""
        {}

        {} を押すと集計結果を発表します！
    """).format(
        '\n'.join(f'{emoji} {candidate}' for candidate, emoji in zip(candidates, used_emojis)),
        poll_close_emoji,
    )
    reply: Message = await channel.send(text)
    poll_state = PollState(candidates=candidates, message=reply)

    for emoji in used_emojis:
        await reply.add_reaction(emoji) # TODO: 並列化
    await reply.add_reaction(poll_close_emoji)

class PollResultItem(NamedTuple):
    index: int
    name: str
    users: List[Union[Member, User]]

async def create_poll_result_item(reaction: Reaction, candidates: List[str]) -> Optional[PollResultItem]:
    if reaction.emoji in number_emojis:
        index = number_emojis.index(reaction.emoji)
        if index < len(candidates):
            users = [user for user in await reaction.users().flatten() if not user.bot]
            return PollResultItem(
                index=index,
                name=candidates[index],
                users=users,
            )

async def calculate_poll_result(reactions: List[Reaction], candidates: List[str]) -> List[PollResultItem]:
    items: List[PollResultItem] = filter(
        lambda item: item is not None,
        await asyncio.gather(*[
            create_poll_result_item(reaction, candidates) for reaction in reactions
        ])
    )

    return sorted(items, key=lambda item: item.index)

async def respond_to_poll_close_reaction(reaction: Reaction, user: Union[Member, User]):
    global poll_state

    if poll_state is None:
        return
    if reaction.message.id != poll_state.message.id:
        return
    if reaction.emoji != poll_close_emoji:
        return

    message: Message = reaction.message
    result = await calculate_poll_result(message.reactions, poll_state.candidates)

    result_text = '\n'.join([f'{item.name} {" ".join([user.mention for user in item.users])}' for item in result])

    text = textwrap.dedent("""
        {0}{0}結果発表{0}{0}

        {1}
    """).format(
        emojize(":tada:", True),
        result_text,
    )

    await poll_state.message.channel.send(text)

class EventHandler(NamedTuple):
    on_mention: List[Callable[[Message], Awaitable[None]]]
    on_reaction_add: List[Callable[[Reaction, Union[Member, User]], Awaitable[None]]]

handlers = EventHandler(
    on_mention=[reply_to_odai_request_add, reply_to_poll_request_add, reply_select_to_select_request],
    on_reaction_add=[respond_to_selection_reaction, respond_to_poll_close_reaction],
)
