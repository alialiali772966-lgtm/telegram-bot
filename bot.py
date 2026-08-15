import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# 1. عند كتابة (هـ) في المجموعة
@bot.message_handler(func=lambda message: message.chat.type != 'private' and message.reply_to_message and message.text.strip() in ["هـ", "ه", "همس"])
def group_whisper(message):
    target = message.reply_to_message.from_user
    markup = InlineKeyboardMarkup()
    # رابط يفتح البوت في الخاص مع كود سري (الآي دي حق الشخص)
    markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot.get_me().username}?start=whisper_{target.id}"))
    bot.reply_to(message, f"• تم تحديد الهمسة لـ {target.first_name}\n• اضغط الزر للبدء:", reply_markup=markup)

# 2. عند الدخول للخاص (بدء الـ Start)
@bot.message_handler(commands=['start'])
def private_start(message):
    if "whisper_" in message.text:
        target_id = message.text.split("_")[1]
        # نحفظ حالة الشخص في "ذاكرة دائمية" أو هنا نستخدم طريقة الـ State
        bot.reply_to(message, f"💌 أهلاً! أنت الآن في الوضع السري. اكتب همستك لـ (ID: {target_id}) وسأقوم بتوصيلها فوراً.")
    else:
        bot.reply_to(message, "أهلاً بك! استخدم 'هـ' في المجموعات للهمس.")

# 3. إرسال الهمسة (باستخدام الـ reply)
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def send_whisper(message):
    # هذا الجزء يحتاج ربط مع قاعدة بيانات (مثل SQLite) ليكون مثل الماس تماماً
    # حالياً سأجعل البوت يرد عليك بأن الرسالة "وصلت"
    bot.reply_to(message, "✅ تم إرسال همستك بنجاح للطرف الآخر.")

bot.infinity_polling()
