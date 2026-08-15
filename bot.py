import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

OWNER_ID = 6312345678  # آي دي حسابك

# قاموس لتخزين الجلسات المؤقتة
active_sessions = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    text = message.text
    
    if " " in text:
        payload = text.split(" ", 1)[1]
        
        if payload.startswith("whisper_"):
            try:
                target_id = int(payload.replace("whisper_", ""))
                
                # حفظ الـ chat_id الخاص بالمجموعة اللي انضغط منها الزر
                active_sessions[message.from_user.id] = {
                    'target_id': target_id,
                    'chat_id': message.chat.id
                }
                
                bot.reply_to(message, "💌 • أهلاً! أنت الآن في الوضع السري. اكتب همستك وسأقوم بإرسالها فوراً للقروب:")
                return
            except Exception as e:
                print(f"Error: {e}")

    bot.reply_to(message, "✨ أهلاً بك! استخدم 'هـ' في المجموعات للهمس.")

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private(message):
    user_id = message.from_user.id
    
    if user_id in active_sessions:
        session = active_sessions[user_id]
        target_id = session['target_id']
        chat_id = session['chat_id']
        whisper_text = message.text.strip()
        
        # إنشاء زر رؤية الهمسة في القروب
        markup = InlineKeyboardMarkup()
        # زر يفتح البوت لقراءة الهمسة (أو كـ زر تفاعلي)
        markup.add(InlineKeyboardButton("🛡️ اضغط هنا لقراءة الهمسة", url=f"https://t.me/{bot.get_me().username}?start=readwhisper"))
        
        # 1. إرسال الهمسة للمجموعة (هنا كان النقص بالصيغة القديمة)
        bot.send_message(
            chat_id,
            f"• الهمسة لـ ⟵ [مستخدم](tg://user?id={target_id})\n"
            f"• من ⟵ {message.from_user.first_name}\n"
            f"💌 **النص:** {whisper_text}\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # 2. تأكيد الإرسال في الخاص لك
        bot.reply_to(message, "✅ تم إرسال همستك بنجاح وظهورت في المجموعة!")
        
        # 3. نسخة سريعة للمالك
        try:
            bot.send_message(OWNER_ID, f"🚨 همسة سرية جديدة:\nمن: {message.from_user.first_name}\nالنص: {whisper_text}")
        except:
            pass
            
        # مسح الجلسة بعد الإرسال
        del active_sessions[user_id]
    else:
        bot.reply_to(message, "الرجاء الذهاب للمجموعة والرد بـ (هـ) على الشخص ثم الضغط على زر (اهمس هنا) أولاً.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def handle_group(message):
    if message.reply_to_message and message.text.strip() in ["هـ", "ه", "همس", "اهمس"]:
        target = message.reply_to_message.from_user
        if target.is_bot:
            return
            
        markup = InlineKeyboardMarkup()
        bot_user = bot.get_me().username
        
        markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot_user}?start=whisper_{target.id}"))
        
        bot.reply_to(
            message,
            f"• تم تحديد الهمسه لـ ⟵ [{target.first_name}](tg://user?id={target.id})\n• اضغط الزر لكتابة الهمسة في الخاص\n-",
            parse_mode="Markdown"
        )

bot.infinity_polling()
