# channel_handler

## 概要
チャンネルごとに状態を持つ機能について，イベントを受け取り適切な処理を行う．

## クラスの役割
- `ChannelState`
  + ある 1 つのチャンネルの現在の状態を表す
    + bot がとりうる状態 1 つに対し，`ChannelState` の派生クラス 1 つが対応する
  + チャンネルでイベントが発生した場合に，返答等を行った後，次の状態を出力する
- `ChannelContext`
  + 1 つのチャンネルが持つ状態のうち，`ChannelState` のどの派生クラスでも同じ値を持つ情報を保持する
- `ChannelsEventHandler`
  + Discord 全体のイベントを受け取り，イベントが発生したチャンネルに紐づく `ChannelState` にイベントを送信する

## クラス間の関係
- `ChannelEventHandler` インスタンスはチャンネル 1 つにつき `ChannelState` インスタンス 1 つを持つ
  + （補足）ただし，Discord のチャンネルは無数に存在し，全てのチャンネルの状態を記憶することは困難．  
  そこで，「待機状態」を表す `StandByState` と，`ChannelEventHandler` インスタンスが当該チャンネルに紐づく `ChannelState` インスタンスを持たないことを同一視する．  
  つまり，記憶しておくのは「待機状態」以外の状態になっているチャンネルの状態のみ．
- `ChannelState` インスタンスは `ChannelContext` インスタンスを 1 つ持つ
- `ChannelEventHandler` インスタンスが `discord.py` からイベントを受け取ると
  + `ChannelEventHandler` インスタンスはイベントが発生したチャンネルに紐づく `ChannelState` インスタンスの `on_イベント名` メソッドを呼び出すことでイベントを当該 `ChannelState` インスタンスに伝える
  + `ChannelState` インスタンスの `on_イベント名` メソッドはイベントを適切に処理（返答メッセージ送信など）を行い，イベントの結果次に遷移する状態を表す `ChannelState` インスタンスを `return` する
  + `ChannelEventHandler` インスタンスは `on_イベント名` の返り値を受け取り，当該チャンネルに紐づいている `ChannelState` インスタンスを変更する

![クラス図](../../images/icebreak_bot/channel_handler/classes.png)
クラス図

![イベント通知の流れ](../../images/icebreak_bot/channel_handler/event.png)
イベント通知の流れ

## 状態遷移図
![](../../images/icebreak_bot/channel_handler/states.png)

## 永続化
`ChannelEventHandler` の `channel_states` をいい感じに DB に保存すればよさそう．
