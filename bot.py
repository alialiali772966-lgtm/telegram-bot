import os
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "I am alive"
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# التوكن الصحيح من الصورة
token = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(token)

# الآيدي الخاص بك كمشرف ومالك للبوت
ADMIN_ID = 6641182392

whisper_data = {}        
active_whispers = {}     

@bot.message_handler(commands=['start'])
def start(message):
    text = message.text
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if text and text.startswith("/start whisper_"):
        try:
            parts = text.replace("/start whisper_", "").split("_")
            target_id = int(parts[0])
            group_id = int(parts[1]) if len(parts) > 1 else None
            
            if user_id == target_id:
                bot.send_message(chat_id, "⚠️ عذراً، لا يمكنك إرسال همسة لنفسك! ❌", parse_mode="Markdown")
                return
            
            target_name = "العضو"
            try:
                chat_member = bot.get_chat_member(group_id, target_id)
                target_name = chat_member.user.first_name
            except Exception:
                pass

            whisper_data[user_id] = {
                'target_id': target_id,
                'target_name': target_name,
                'group_chat_id': group_id
            }
            bot.send_message(chat_id, f"💌 • اكتب همستك لـ *{target_name}* الآن:", parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, f"💌 • اكتب همستك الشخصية الآن:")
        return

    bot_username = bot.get_me().username
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ اضفني لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=true"))
    
    welcome_text = (
        "✨ • أهلاً بك في بوت الهمسات الذكي\n\n"
        "🛡️ • يمكنك من خلالي إرسال همسات سرية وآمنة داخل المجموعات لأي عضو بالرد على رسالته.\n\n"
        "💡 • طريقة الاستخدام:\n"
        "• رد على رسالة أي شخص في المجموعة بكلمة (همس) أو حرف (هـ)\n"
        "• اضغط على زر (اهمس هنا) المظهر واكتب همستك بكل سرية!"
    )
    
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def handle_group_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    if not message.reply_to_message or not text:
        return

    clean_text = text.strip()
    if not (clean_text.startswith("همس") or clean_text.startswith("هـ") or clean_text.startswith("ه") or clean_text.startswith(".")):
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
        f"• تم تحديد الهمسة لـ ⟵ {target_mention}\n• اضغط الزر لكتابة الهمسة في الخاص:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    if not text or text.startswith('/'):
        return

    target_info = whisper_data.get(user_id)
    if target_info:
        target_name = target_info.get('target_name', 'العضو')
        target_id = target_info['target_id']
        group_id = target_info.get('group_chat_id')
        sender_name = message.from_user.first_name
        sender_id = message.from_user.id
        
        if user_id == target_id:
            bot.send_message(chat_id, "⚠️ لا يمكنك إرسال همسة لنفسك.")
            del whisper_data[user_id]
            return

        if not group_id:
            bot.send_message(chat_id, "⚠️ عذراً، يرجى استخدام زر الهمسة من داخل المجموعة مباشرة.")
            return

        whisper_id = f"{user_id}_{target_id}_{message.message_id}"
        
        active_whispers[whisper_id] = {
            'text': text,
            'sender_name': sender_name,
            'sender_id': user_id,
            'target_id': target_id,
            'target_name': target_name,
            'read_status': False
        }
        
        target_mention = f"[{target_name}](tg://user?id={target_id})"
        sender_mention = f"[{sender_name}](tg://user?id={sender_id})"
        
        group_markup = InlineKeyboardMarkup()
        group_markup.row(InlineKeyboardButton("🔐 رؤية الهمسة", callback_data=f"read_{whisper_id}"))
        group_markup.row(InlineKeyboardButton(f"💬 اهمس لـ {sender_name} مباشرة", url=f"https://t.me/{bot.get_me().username}?start=whisper_{user_id}_{group_id}"))
        
        bot.send_message(
            group_id,
            f"• الهمسه لـ ⟵ {target_mention}\n• من ⟵ {sender_mention}\n-",
            reply_markup=group_markup,
            parse_mode="Markdown"
        )
        
        bot.send_message(chat_id, f"✨ • تم ارسال همستك إلى المجموعة بنجاح!", parse_mode="Markdown")
        
        del whisper_data[user_id]
    else:
        bot.send_message(chat_id, "⚠️ الرجاء استخدام أزرار الهمسات في المجموعة أولاً بالرد على رسالة الشخص.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("read_"))
def read_whisper_callback(call):
    user_id = call.from_user.id
    whisper_id = call.data.replace("read_", "")
    
    whisper_info = active_whispers.get(whisper_id)
    
    if not whisper_info:
        bot.answer_callback_query(call.id, "⚠️ انتهت صلاحية هذه الهمسة أو غير موجودة.", show_alert=True)
        return

    target_id = whisper_info['target_id']
    sender_id = whisper_info['sender_id']
    whisper_text = whisper_info['text']
    target_name = whisper_info['target_name']
    
    if user_id == target_id or user_id == sender_id or user_id == ADMIN_ID:
        bot.answer_callback_query(
            call.id,
            f"{whisper_text}\n\n- الصفحة 1 / 1 📄",
            show_alert=True
        )
        
        if user_id == target_id and not whisper_info['read_status']:
            whisper_info['read_status'] = True
            try:
                bot.send_message(
                    sender_id,
                    f"• تمت قراءة الهمسة .. بنجاح\n• بواسطة العضو المطلوب ✨\n- من قبل ⟵ *{target_name}*",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print("Error:", e)
    else:
        bot.answer_callback_query(
            call.id,
            "عذراً، هذه الهمسة ليست موجهة لك 🔒",
            show_alert=True
        )

print("Bot is running perfectly...")
bot.infinity_polling(skip_pending=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
