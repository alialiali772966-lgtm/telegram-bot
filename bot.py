import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# استخدام التوكن الجديد الآمن
TOKEN = '8912650382:AAGxGtTJ6loePuG3Dyt3f8Knhpa4HGDR4A'
bot = telebot.TeleBot(TOKEN)

# درس البداية
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("إرسال همسة 🤫", callback_data="send_whisper"))
    bot.reply_to(message, "مرحباً بك في بوت حماية وخدمات رينكس. اضغط بالأسفل لإرسال همسة خاصة:", reply_markup=markup)

# التعامل مع الضغط على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "send_whisper":
        # يمكنك هنا استقبال الهمسة أو إرسال تنبيه للمستخدم بشكل مؤقت
        bot.answer_callback_query(call.id, "تم فتح نافذة الهمسة السرية 🤫", show_alert=False)
        
        # مثال على رسالة مؤقتة أو تختفي:
        # ملاحظة: تليجرام لا يدعم حذف رسائل المستخدم نفسه مباشرة، ولكن يمكن للبوت حذف رده أو تعديله فوراً
        bot.send_message(call.message.chat.id, "اكتب همستك الآن (هذه الرسالة ستكون مخفية أو خاصة)...")

# تشغيل البوت بشكل دائم وآمن
print("Bot is running...")
bot.infinity_polling()
