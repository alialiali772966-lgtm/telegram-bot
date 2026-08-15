@bot.message_handler(func=lambda message: message.chat.type != 'private')
def handle_group_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    if not message.reply_to_message or not text:
        return

    clean_text = text.strip()
    # هنا الشرط صار دقيق:只要 تكتب (هـ) أو (ه) أو (همس) راح يشتغل فوراً
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
        f"• تم تحديد الهمسة لـ ⟵ {target_mention}\n• اضغط الزر لكتابة الهمسة في الخاص:",
        reply_markup=markup,
        parse_mode="Markdown"
    )
