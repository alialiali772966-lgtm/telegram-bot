import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# تخزين مؤقت للهمسات والجلسات
database = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    text = message.text
    
    if " " in text:
        payload = text.split(" ", 1)[1]
        
        # 1. عند الضغط على "اهمس هنا" في القروب والانتقال للخاص
        if payload.startswith("whisper_"):
            target_name = payload.replace("whisper_", "").strip()
            database[message.from_user.id] = {
                'target_name': target_name,
                'chat_id': message.chat.id,
                'step': 'waiting_for_whisper'
            }
            # يرسل في الخاص تماماً مثل بوت الماس:
            bot.reply_to(message, f"• 💌 • اكتب همستك لـ 🪶 **{target_name}** الآن:", parse_mode="Markdown")
            return
            
        # 3. عند الضغط على زر "رؤية الهمسة 🔒" في القروب
        elif payload.startswith("read_"):
            w_id = payload.replace("read_", "").strip()
            if w_id in database:
                item = database[w_id]
                
                # إظهار الهمسة للشخص الذي قام بقراءتها
                bot.reply_to(
                    message,
                    f"✨ **تمت قراءة الهمسة .. بنجاح**\n"
                    f"• من قبل ← {item['sender_name']}\n"
                    f"• إلى ← {item['target_name']}\n\n"
                    f"💌 **النص:**\n{item['text']}",
                    parse_mode="Markdown"
                )
                
                # إرسال إشعار للمرسل أن همسته انقرأت
                try:
                    bot.send_message(
                        item['sender_id'],
                        f"👁️‍🗨️ • تم قراءة همستك إلى 🪶 {item['target_name']} بنجاح!"
                    )
                except:
                    pass
            else:
                bot.reply_to(message, "⚠️ عذراً، انتهت صلاحية هذه الهمسة أو تمت قراءتها مسبقاً.")
            return

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
    
    # 2. استقبال الهمسة بعد كتابتها وإرسالها في الخاص
    if user_id in database and database[user_id].get('step') == 'waiting_for_whisper':
        session = database[user_id]
        whisper_text = message.text.strip()
        
        # إنشاء معرف فريد للهمسة بناءً على الوقت أو رقم الرسالة
        w_id = f"w_{user_id}_{message.message_id}"
        
        database[w_id] = {
            'text': whisper_text,
            'sender_id': user_id,
            'sender_name': message.from_user.first_name,
            'target_name': session['target_name']
        }
        
        # تجهيز الأزرار تحت الهمسة في المجموعة
        markup = InlineKeyboardMarkup()
        bot_user = bot.get_me().username
        markup.add(InlineKeyboardButton("🔒 رؤية الهمسة", url=f"https://t.me/{bot_user}?start=read_{w_id}"))
        markup.add(InlineKeyboardButton(f"اهمس لـ {session['target_name']} 💬", url=f"https://t.me/{bot_user}?start=whisper_{session['target_name']}"))
        
        # إرسال الهمسة للمجموعة
        bot.send_message(
            session['chat_id'],
            f"• الهمسه لـ ⟵ 🪶 {session['target_name']}\n• من ⟵ {message.from_user.first_name}\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # رد البوت في الخاص (يطابق طلبك تماماً)
        bot.reply_to(message, f"• تم ارسال همستك لـ 🪶 {session['target_name']} بنجاح ✨")
        
        # تنظيف الجلسة المؤقتة
        del database[user_id]
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
            f"• تم تحديد الهمسه لـ ⟵ 🪶 {target_name}\n• اضغط الزر لكتابة الهمسة\n-",
            parse_mode="Markdown"
        )

bot.infinity_polling()
