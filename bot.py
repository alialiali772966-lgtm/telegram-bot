import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# تخزين مؤقت لجلسات الهمس النشطة
active_whispers = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    text = message.text
    
    if " " in text:
        payload = text.split(" ", 1)[1]
        
        # عند الضغط على زر "اهمس هنا" من المجموعة والانتقال للخاص
        if payload.startswith("whisper_"):
            target_name = payload.replace("whisper_", "")
            active_whispers[message.from_user.id] = {
                'target_name': target_name,
                'chat_id': message.chat.id
            }
            bot.reply_to(message, f"• 💌 • اكتب همستك لـ **{target_name}** الآن:", parse_mode="Markdown")
            return
            
        # عند الضغط على زر "رؤية الهمسة"
        elif payload.startswith("read_"):
            w_id = payload.replace("read_", "")
            if w_id in active_whispers:
                w = active_whispers[w_id]
                bot.reply_to(
                    message,
                    f"• تمت قراءة الهمسة .. بنجاح\n• بواسطة العضو المطلوب ✨\n- من قبل ← {w['sender_name']}♡\n\n💌 **النص:**\n{w['text']}",
                    parse_mode="Markdown"
                )
            else:
                bot.reply_to(message, "⚠️ عذراً، انتهت صلاحية هذه الهمسة أو تمت قراءتها مسبقاً.")
            return

    # الرسالة الترحيبية الافتراضية
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
def handle_private(message):
    user_id = message.from_user.id
    
    if user_id in active_whispers and 'target_name' in active_whispers[user_id] and 'text' not in active_whispers[user_id]:
        session = active_whispers[user_id]
        whisper_text = message.text.strip()
        
        # حفظ نص الهمسة واسم المرسل
        w_id = f"{user_id}_{message.message_id}"
        active_whispers[w_id] = {
            'text': whisper_text,
            'sender_name': message.from_user.first_name,
            'target_name': session['target_name']
        }
        
        # إنشاء الأزرار الموجودة في الصورة المطلوبة (رؤية الهمسة + اهمس مباشرة)
        markup = InlineKeyboardMarkup()
        bot_user = bot.get_me().username
        markup.add(InlineKeyboardButton("رؤية الهمسة 🔒", url=f"https://t.me/{bot_user}?start=read_{w_id}"))
        markup.add(InlineKeyboardButton(f"اهمس لـ {session['target_name']} مباشرة 💬", url=f"https://t.me/{bot_user}?start=whisper_{session['target_name']}"))
        
        # إرسال الهمسة للمجموعة بالصيغة تماماً كما في الصورة
        bot.send_message(
            session['chat_id'],
            f"• الهمسه لـ ⟵ {session['target_name']}\n• من ⟵ {message.from_user.first_name}\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # تأكيد الإرسال في الخاص
        bot.reply_to(message, "• تم ارسال همستك إلى المجموعة بنجاح ✨")
        
        # تنظيف الجلسة المؤقتة
        del active_whispers[user_id]
    else:
        bot.reply_to(message, "✨ أهلاً بك! استخدم الرمز (هـ) بالرد على أي شخص داخل المجموعة للبدء بالهمس.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def handle_group(message):
    if message.reply_to_message and message.text.strip() in ["هـ", "ه", "همس", "اهمس"]:
        target = message.reply_to_message.from_user
        if target.is_bot:
            return
            
        markup = InlineKeyboardMarkup()
        bot_user = bot.get_me().username
        target_name = target.first_name
        
        markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot_user}?start=whisper_{target_name}"))
        
        bot.reply_to(
            message,
            f"• تم تحديد الهمسه لـ ⟵ {target_name}\n• اضغط الزر لكتابة الهمسة\n-",
            parse_mode="Markdown"
        )

bot.infinity_polling()
