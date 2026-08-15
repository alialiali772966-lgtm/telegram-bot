@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_messages(message):
    user_id = message.from_user.id
    text = message.text

    # تأكد أن البوت يقرأ النص بشكل صحيح
    if not text or text.startswith('/'):
        return

    target_info = whisper_data.get(user_id)
    if target_info:
        # تأكد من أن النص موجود قبل الإرسال
        whisper_text = text.strip()
        
        # حفظ الهمسة في الذاكرة بشكل أدق
        whisper_id = f"{user_id}_{target_info['target_id']}_{message.message_id}"
        active_whispers[whisper_id] = {
            'text': whisper_text,
            'sender_name': message.from_user.first_name,
            'target_id': target_info['target_id'],
            'target_name': target_info['target_name'],
            'read_status': False
        }
        
        # (بقية الكود الخاص بإرسال الإشعار للمجموعة...)
        # تأكد أنك تستخدم نفس الـ whisper_id عند عرض الهمسة
