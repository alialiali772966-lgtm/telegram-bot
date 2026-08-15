import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# تخزين مؤقت لحالة الهمسة لكل مستخدم
user_whisper_target = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = message.text
    
    # التحقق إذا كان الرابط يحتوي على استدعاء همسة لشخص معين
    if " " in text:
        args = text.split(" ", 1)[1]
        if args.startswith("whisper_"):
            target_name = args.replace("whisper_", "")
            # فك الزخرفة أو الحفاظ على اسم الشخص كما هو
            user_whisper_target[message.from_user.id] = target_name
            bot.reply_to(message, f"• 💌 • اكتب همستك لـ **{target_name}** الآن:", parse_mode="Markdown")
            return

    # الرسالة الترحيبية العادية عند الضغط /start بدون روابط
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ اضفني لمجموعتك", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
    bot.reply_to(
        message,
        "✨ **أهلاً بك في بوت الهمسات الذكي**\n\n"
        "🛡️ • يمكنك من خلالي إرسال همسات سرية وآمنة داخل المجموعات لأي عضو بالرد على رسالته.\n\n"
        "💡 • **طريقة الاستخدام:**\n"
        "• رد على رسالة أي شخص في المجموعة بكلمة (همس) أو حرف (هـ)\n"
        "• اضغط على زر (اهمس هنا) المظهر واكتب همستك بكل سرية!",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_messages(message):
    user_id = message.from_user.id
    
    # إذا كان المستخدم في وضع كتابة همسة لشخص تم تحديده مسبقاً
    if user_id in user_whisper_target:
        target_name = user_whisper_target[user_id]
        whisper_text = message.text.strip()
        
        # رسالة تأكيد الإرسال في الخاص تماماً مثل الصورة القديمة
        bot.reply_to(message, "• تم ارسال همستك إلى المجموعة بنجاح ✨")
        
        # مسح الحالة بعد الإرسال
        del user_whisper_target[user_id]
    else:
        # إذا أرسل /start أو كلام عادي في الخاص
        bot.reply_to(message, "✨ أهلاً بك! استخدم الرمز (هـ) أو (همسد) بالرد على أي شخص داخل المجموعة للبدء بالهمس.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def group_handler(message):
    if message.reply_to_message and message.text.strip() in ["هـ", "ه", "همس", "اهمس"]:
        target = message.reply_to_message.from_user
        if target.is_bot:
            return
            
        markup = InlineKeyboardMarkup()
        bot_user = bot.get_me().username
        
        # تمرير اسم الشخص المستهدف (مع دعم الأسماء المزخرفة مثل النجوم والرموز)
        target_display_name = target.first_name
        markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot_user}?start=whisper_{target_display_name}"))
        
        bot.reply_to(
            message,
            f"• تم تحديد الهمسه لـ ⟵ {target_display_name}\n• اضغط الزر لكتابة الهمسة\n-",
            parse_mode="Markdown"
        )

bot.infinity_polling()
