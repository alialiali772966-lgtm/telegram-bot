import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توكن البوت الخاص بك
TOKEN = "8912650382:AAFlhp_GOmLRGuAr_Ft3L2we4JRHxntvRpw"
bot = telebot.TeleBot(TOKEN)

# قواميس لحفظ بيانات الهمسات المؤقتة
whisper_data = {}
active_whispers = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = message.text
    if len(text.split()) > 1:
        param = text.split()[1]
        if param.startswith("whisper_"):
            try:
                _, target_id_str, chat_id_str = param.split("_")
                target_id = int(target_id_str)
                sender_id = message.from_user.id
                
                # التحقق أن الشخص الموجهة له الهمسة هو من فتح الرابط
                if sender_id != target_id:
                    bot.send_message(message.chat.id, "❌ عذراً، هذه الهمسة ليست موجهة لك!")
                    return
                
                # البحث عن الهمسة بناءً على معرف المستقبل
                found_whisper = None
                for w_id, w_data in active_whispers.items():
                    if w_data['target_id'] == target_id and not w_data['read_status']:
                        found_whisper = w_data
                        break
                
                if found_whisper:
                    found_whisper['read_status'] = True
                    sender_name = found_whisper['sender_name']
                    whisper_content = found_whisper['text']
                    
                    bot.send_message(
                        message.chat.id,
                        f"📬 **وصلتك همسة جديدة!**\n\n👤 من: {sender_name}\n💬 النص:\n{whisper_content}",
                        parse_mode="Markdown"
                    )
                else:
                    bot.send_message(message.chat.id, "⚠️ عذراً، هذه الهمسة غير موجودة أو تم قراءتها مسبقاً.")
                return
            except Exception as e:
                bot.send_message(message.chat.id, "❌ حدث خطأ أثناء فتح الهمسة.")
                return

    bot.send_message(message.chat.id, "✨ أهلاً بك في بوت الهمسات. البوت يعمل بكفاءة وجاهز لتلقي الهمسات في المجموعات والتعليقات.")

# استقبال الهمسة المكتوبة في الخاص
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
            'target_name': target_info['target_name'],
            'read_status': False
        }
        
        markup = InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        markup.add(InlineKeyboardButton("👁️ اضغط هنا لقراءة الهمسة", url=f"https://t.me/{bot_username}?start=whisper_{target_id}_{chat_id}"))
        
        target_mention = f"[{target_info['target_name']}](tg://user?id={target_id})"
        
        bot.send_message(
            chat_id,
            f"• الهمسه لـ ⟵ {target_mention}\n• من ⟵ {message.from_user.first_name}\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        bot.send_message(message.chat.id, "✅ تم إرسال همستك بنجاح إلى المجموعة!")
        del whisper_data[user_id]
    else:
        bot.send_message(message.chat.id, "الرجاء الرد بكلمة (هـ) على الشخص الذي تريد مراسلته في المجموعة أو التعليقات أولاً.")

# استقبال الردود في المجموعات وتعليقات القنوات
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
    markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot_username}?start=whisper_{target_user_id}_{chat_id}"))
    
    target_mention = f"[{target_user_name}](tg://user?id={target_user_id})"
    
    bot.reply_to(
        message,
        f"• تم تحديد الهمسه لـ ⟵ {target_mention}\n• اضغط الزر لكتابة الهمسة في الخاص",
        reply_markup=markup,
        parse_mode="Markdown"
    )

bot.infinity_polling()
