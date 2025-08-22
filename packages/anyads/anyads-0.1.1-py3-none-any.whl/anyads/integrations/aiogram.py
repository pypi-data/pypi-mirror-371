# src/anyads/integrations/aiogram.py

try:
    from aiogram import Dispatcher, types
    from anyads import get_sdk_instance, InitializationError
except ImportError:
    class Dispatcher: pass
    class types: pass

def register_anyads_handlers(dp: Dispatcher):
    """
    Функция-хелпер для автоматической регистрации обработчика
    верификационной команды в aiogram.
    
    Для использования установите SDK с поддержкой aiogram:
    pip install "anyads[aiogram]"
    """
    try:
        sdk = get_sdk_instance()
    except InitializationError as e:
        raise InitializationError(
            "AnyAds SDK не был инициализирован. "
            "Вызовите anyads.init() перед регистрацией обработчиков."
        ) from e


    @dp.message(lambda msg: msg.text and msg.text.startswith('/verify_anyads_'))
    async def _handle_verification_command(message: types.Message):
        success = await sdk.process_verification_code(message.text)
        
        if success:
            await message.answer("✅ Верификация SDK AnyAds успешно пройдена!")
        else:
            await message.answer("❌ Произошла ошибка во время верификации. Попробуйте снова или обратитесь в поддержку.")