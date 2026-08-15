import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# تخزين بيانات الهمسة الحالية لكل مستخدم
user_states = {}
active_whispers = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("whisper_"):
        whisper_id = args[1].replace("whisper_", "")
        if whisper_id in active_whispers:
            w = active_whispers[whisper_id]
            if w['read_status']:
                bot.reply_to(message, "⚠️ عذراً، هذه الهمسة تمت قراءتها مسبقاً.")
            else:
                w['read_status'] = True
                bot.reply_to(message, f"• تمت قراءة الهمسة .. بنجاح\n• بواسطة العضو المطلوب ✨\n- من قبل ← {w['sender_name']}♡\n\n💌 النص:\n{w['text']}")
            return
    
    # الرسالة الترحيبية المعتادة
    bot.reply_to(message, "✨ أهلاً بك في بوت الهمسات الذكي.\n\n💡 للبدء، رد على أي رسالة بـ (همس) في المجموعة.")

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
            'read_status': False
        }
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👁️ اضغط هنا لقراءة الهمسة", url=f"https://t.me/{bot.get_me().username}?start=whisper_{whisper_id}"))
        
        bot.send_message(target['chat_id'], f"• تم تحديد الهمسة لـ ⟵ [{target['name']}](tg://user?id={target['target_id']})\n• من ⟵ {message.from_user.first_name}\n-", reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(message, "✨ • تم ارسال همستك إلى المجموعة بنجاح!")
        del user_states[user_id]
    else:
        bot.reply_to(message, "الرجاء الرد بكلمة (همس) على الشخص في المجموعة أولاً.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def group_chat(message):
    if not message.reply_to_message or message.text not in ["هـ", "ه", "همس"]:
        return
        
    target = message.reply_to_message.from_user
    user_states[message.from_user.id] = {
        'target_id': target.id,
        'name': target.first_name,
        'chat_id': message.chat.id
    }
    
    bot.reply_to(message, f"• اكتب همستك لـ {target.first_name} الآن في الخاص:")

bot.infinity_polling()
