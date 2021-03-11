# インストールした discord.py を読み込む
import discord
import random
from quart import Quart, request

quart = Quart(__name__)

# テスト用にチャンネルIDを設定している
# 今後は動的にチャンネルを動的に取得する必要がある
# よくあるのがherokuの環境変数に設定する方法らしい
# セキュリティ上IDは削除
CHANNEL_ID =   # 任意のチャンネルID(int)
# 接続に必要なオブジェクトを生成
intents = discord.Intents().default()
intents.members = True
client = discord.Client(intents=intents)

emoji = '\N{Face with Party Horn and Party Hat}'

# 任意のチャンネルで挨拶する非同期関数を定義


async def isuue_embed(title, description, login, issue_url, user_url,
                      user_avatar_url):
    channel = client.get_channel(CHANNEL_ID)
    members = get_members(channel)
    embed = discord.Embed(
        title=title,
        description=description +
        "\nやってくれるね？" +
        random.choice(members).mention,
        url=issue_url)
    # ここ以降にフォーマットの改変を記載
    embed.set_author(name=login, url=user_url, icon_url=user_avatar_url)
    await channel.send(embed=embed)


# tmp_commit = dict()
# tmp_commit["id"] = str(commit["id"])[0:6]
# tmp_commit["url"] = commit["url"]
# tmp_commit["message"] = commit["message"]
# # commitとauthorのどちらがいいか判断がつかない。一時的にauthorにする
# tmp_commit["name"] = commit["author"]["name"]
# commits_info.append(tmp_commit)
async def push_embed(title, sender_login, commits_info, push_url,
                     sender_url, sender_avatar_url):
    channel = client.get_channel(CHANNEL_ID)
    # ここ以降にフォーマットの改変を記載
    # titleに埋め込みURLは["commits"]["url"]
    # 本文の16進数は["commits"]["id"]の先頭7文字
    # icon_urlは["sender"]["avatar_url"]
    description = str()
    pushers = set()
    for commit_info in commits_info:
        description += "\n[" + commit_info["id"] + "]" + \
            "(" + commit_info["url"] + ") " + \
            commit_info["message"] + " - " + \
            commit_info["name"]
        pushers.add(commit_info["name"])
    praise = str()
    praise = '\n\n'
    for pusher in pushers:
        praise += pusher + "さん、"
    praise += "偉い偉い偉い！！！" + emoji
    embed = discord.Embed(title=title,
                          description=description + praise, url=push_url)
    embed.set_author(name=sender_login, url=sender_url,
                     icon_url=sender_avatar_url)
    await channel.send(embed=embed)


# ngrokでもできるが、デプロイのほうが楽
# githubからのjsonはheoku localではなく、デプロイをする必要がある。
@quart.route('/gh-webhook', methods=['POST'])
async def webhook():
    # print(request)              # requestにjsonが入っている
    json = await request.get_json()
    header = request.headers
    event_type = header["X-Github-Event"]
    # eventごとに分別
    title = str()
    description = str()
    # issueの場合
    if event_type == "issues":
        data = json["issue"]
        title = "[" + json["repository"]["full_name"] + "] issue " \
            + json["action"] + ": #" + str(data["number"]) + " " + \
            data["title"]
        description = data["body"]
        login = data["user"]["login"]
        isuue_url = data["html_url"]
        user_avatar_url = data["user"]["avatar_url"]
        user_url = data["user"]["html_url"]
        await isuue_embed(title, description, login,
                          isuue_url, user_url, user_avatar_url)
    # pushの場合
    elif event_type == "push":
        data = json["commits"]
        # title = str(data[0]["id"])
        # master_branchなのかdefault_branchなのかの判断がつかない
        commits_number = str(len(data))
        title = "[" + json["repository"]["name"] + ":" + \
            json["repository"]["master_branch"] + "] " + commits_number + \
            " new commit"
        push_url = json["compare"]
        description = data[0]["message"]
        sender = json["sender"]
        commits_number = len(data)
        sender_login = sender["login"]
        sender_url = sender["html_url"]
        sender_avatar_url = sender["avatar_url"]
        commits_info = list()
        for commit in data:
            tmp_commit = dict()
            tmp_commit["id"] = str(commit["id"])[0:6]
            tmp_commit["url"] = commit["url"]
            tmp_commit["message"] = commit["message"]
            # commiterとauthorのどちらがいいか判断がつかない。一時的にauthorにする
            tmp_commit["name"] = commit["author"]["name"]
            commits_info.append(tmp_commit)
        print(commits_info)
        await push_embed(title, sender_login, commits_info, push_url,
                         sender_url, sender_avatar_url)
    return '', 200


# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        #         await message.add_reaction(emoji)
        return
    if message.content == 'github リアクション':
        await message.channel.send('github リアクションつける')
#         await message.add_reaction(emoji)
# チャンネルIDをチェックするため 
    elif message.content == '/test':
        await message.channel.send('channelID:' + str(message.channel.id))
    # /randと発言したらサーバー内のメンバーから誰かにメンション
    elif message.content == '/rand':
        members = get_members(message.channel)
        await message.channel.send(random.choice(members).mention)


def get_members(channel):
    members = list()
    for member in channel.members:
        if not(member.bot):
            members.append(member)
    return members
