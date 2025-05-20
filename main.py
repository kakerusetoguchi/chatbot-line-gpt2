from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

# 環境変数からキーを取得
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "LINE + ChatGPT bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature. Check your LINE_CHANNEL_SECRET.', 400

    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    messages = [
        {"role": "system", "content": "You are an English teacher helping a Japanese student practice English."},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply_text = response["choices"][0]["message"]["content"]
    except Exception as e:
        reply_text = f"Error from OpenAI: {str(e)}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
