import os
import telebot
from flask import Flask
from threading import Thread

# توكن بوت رينكس مباشرة
TOKEN = "8912650382:AAF1hp_G0mLRGuAr_Ft3L2we4JRHxntvRpw"
bot = telebot.TeleBot(TOKEN)

# إعداد سيرفر الويب عشان يظل شغال
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت رينكس للهمسات ✨")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
