
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    RichMenu, RichMenuArea,
    RichMenuBounds, RichMenuSize
)

from linebot.models.actions import PostbackAction

import os

app = Flask(__name__)

#herokuの環境変数に設定された、LINE DevelopersのアクセストークンとChannelSecretを
#取得するコード
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

#herokuへのデプロイが成功したかどうかを確認するためのコード
@app.route("/")
def hello_world():
    return "hello world!"


#LINE DevelopersのWebhookにURLを指定してWebhookからURLにイベントが送られるようにする
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名を検証し、問題なければhandleに定義されている関数を呼ぶ
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#RichMenu
rich_menu_to_create = RichMenu(
    size = RichMenuSize(width=2500, height=1686),
    selected = True,
    name = 'richmenu',
    chat_bar_text = 'メニュー',
    areas=[
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1273, height=868),
            action=PostbackAction(data='renew')
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=1278, y=0, width=1211, height=864),
            action=PostbackAction(data='deadline')
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=864, width=1268, height=818),
            action=PostbackAction(data="not_submitted")
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=1273, y=877, width=1227, height=805),
            action=PostbackAction(data="forget")
        )
    ]
)

richMenuId = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
line_bot_api.set_default_rich_menu(richMenuId)


#以下でWebhookから送られてきたイベントをどのように処理するかを記述する
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))



# ポート番号の設定
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)