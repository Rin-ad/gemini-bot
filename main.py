import config
import os
from flask import Flask,request,abort
import google.generativeai as genai

from linebot import (
    LineBotApi,WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent,TextMessage,TextSendMessage,
)

app = Flask(__name__)

gemini = genai.configure(api_key=config.GEMINI_API_KEY)

def get_response(question):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(question)
    return response.text

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    line_bot_api.reply_message (
        event.reply_token,
        TextMessage(text=get_response(event.message.text))
    )

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(host='0.0.0.0',port=port)
    