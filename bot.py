import telebot

TOKEN = '8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! البوت يعمل الآن بشكل صحيح.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()
