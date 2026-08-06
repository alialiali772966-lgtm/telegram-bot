import os
import telebot
from flask import Flask
from threading import Thread

# توكن البوت
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# إعداد سيرفر الويب البسيط عشان رندر ما يعطي Timeout
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    # استخدام البورت اللي يحدده رندر تلقائياً
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت الهمسات الذكي ✨")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
