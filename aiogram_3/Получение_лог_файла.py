@router.message(Command("log"))
async def send_log(message: Message):
    """
    Отправляет логи бота по запросу администратора, прописанного в .env файле
    :param message: Message - сообщение от пользователя
    :return: None
    """
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ запрещен")
        return
    
    log_file = FSInputFile("log/log.log")
    try:
        await message.answer_document(log_file, caption="📄 Логи бота")
    except Exception as e:
        await message.answer(f"❌ Не удалось отправить логи: {str(e)}")