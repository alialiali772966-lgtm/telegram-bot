import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# قواميس لحفظ بيانات الهمسات
whisper_data = {}
active_whispers = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = message.text
    if len(text.split()) > 1:
        param = text.split()[1]
        if param.startswith("whisper_"):
            try:
                whisper_id = param.replace("whisper_", "")
                found_whisper = active_whispers.get(whisper_id)
                
                if found_whisper and not found_whisper['read_status']:
                    found_whisper['read_status'] = True
                    sender_name = found_whisper['sender_name']
                    whisper_content = found_whisper['text']
                    
                    bot.send_message(
                        message.chat.id,
                        f"• تمت قراءة الهمسة .. بنجاح\n• بواسطة العضو المطلوب ✨\n- من قبل ← {sender_name}♡",
                        parse_mode="Markdown"
                    )
                    bot.send_message(
                        message.chat.id,
                        f"💌 **النص:**\n{whisper_content}",
                        parse_mode="Markdown"
                    )
                else:
                    bot.send_message(message.chat.id, "⚠️ عذراً، هذه الهمسة غير موجودة أو تم قراءتها مسبقاً.")
                return
            except Exception as e:
                bot.send_message(message.chat.id, "❌ حدث خطأ أثناء فتح الهمسة.")
                return

    # الرسالة الترحيبية الاحترافية
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ اضفني لمجموعتك", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
    
    bot.send_message(
        message.chat.id,
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
    text = message.text

    if not text or text.startswith('/'):
        return

    target_info = whisper_data.get(user_id)
    if target_info:
        whisper_text = text.strip()
        target_id = target_info['target_id']
        chat_id = target_info['group_chat_id']
        
        whisper_id = f"{user_id}_{target_id}_{message.message_id}"
        active_whispers[whisper_id] = {
            'text': whisper_text,
            'sender_name': message.from_user.first_name,
            'target_id': target_id,
            'read_status': False
        }
        
        markup = InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        # الرابط هنا يرسل معرف الهمسة الصحيح تماماً
        markup.add(InlineKeyboardButton("👁️ اضغط هنا لقراءة الهمسة", url=f"https://t.me/{bot_username}?start=whisper_{whisper_id}"))
        
        target_mention = f"[{target_info['target_name']}](tg://user?id={target_id})"
        
        bot.send_message(
            chat_id,
            f"• تم تحديد الهمسه لـ ⟵ {target_mention}\n• من ⟵ {message.from_user.first_name}\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        bot.send_message(message.chat.id, f"✨ • تم ارسال همستك إلى المجموعة بنجاح!")
        del whisper_data[user_id]
    else:
        bot.send_message(message.chat.id, "الرجاء الرد بكلمة (هـ) على الشخص في المجموعة أولاً لتحديد الهمسة.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def handle_group_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    if not message.reply_to_message or not text:
        return

    clean_text = text.strip()
    if clean_text not in ["هـ", "ه", "همس", "اهمس"]:
        return

    replied_user = message.reply_to_message.from_user
    if replied_user.is_bot:
        return

    target_user_name = replied_user.first_name
    target_user_id = replied_user.id
    
    if user_id == target_user_id:
        return

    whisper_data[user_id] = {
        'target_name': target_user_name,
        'target_id': target_user_id,
        'group_chat_id': chat_id
    }
    
    markup = InlineKeyboardMarkup()
    bot_username = bot.get_me().username
    # تم تصحيح الرابط ليوجه المستخدم للخاص مباشرة بشكل صحيح
    markup.add(InlineKeyboardButton("اهمس هنا ↗️", url=f"https://t.me/{bot_username}?start=whisper_start"))
    
    target_mention = f"[{target_user_name}](tg://user?id={target_user_id})"
    
    bot.reply_to(
        message,
        f"• تم تحديد الهمسه لـ ⟵ {target_mention}\n• اضغط الزر لكتابة الهمسة في الخاص",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    try:
        bot.send_message(user_id, f"💌 • اكتب همستك لـ **{target_user_name}** الآن:", parse_mode="Markdown")
    except:
        pass

bot.infinity_polling()
