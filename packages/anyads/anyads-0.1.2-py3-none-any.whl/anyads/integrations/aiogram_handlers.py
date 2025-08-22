def register(dp):
    """
    Регистрирует обработчики AnyAds для фреймворка Aiogram.
    :param dp: Экземпляр aiogram.Dispatcher
    """
    from aiogram import types
    from anyads import get_sdk_instance, InitializationError

    try:
        sdk = get_sdk_instance()
    except InitializationError as e:
        raise InitializationError(
            "AnyAds SDK не был инициализирован. "
            "Вызовите anyads.init() перед регистрацией обработчиков."
        ) from e

    # Этот хендлер будет зарегистрирован в диспетчере, который передали
    @dp.message(lambda msg: msg.text and msg.text.startswith('/verify_anyads_'))
    async def _handle_verification_command(message: types.Message):
        success = await sdk.process_verification_code(message.text)
        
        if success:
            await message.answer("✅ Верификация SDK AnyAds успешно пройдена!")
        else:
            await message.answer("❌ Произошла ошибка во время верификации. Попробуйте снова или обратитесь в поддержку.")

    # Можно добавить лог для наглядности
    import logging
    logging.getLogger("anyads.sdk").info("Обработчики для Aiogram успешно зарегистрированы.")