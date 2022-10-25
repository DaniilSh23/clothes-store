from aiogram.types import CallbackQuery
from emoji.core import emojize

from keyboards.callback_data_bot import callback_for_next_or_prev_button
from settings.config import DP


async def plug_for_keyboard(call: CallbackQuery):
    '''Заглушка для клавиатуры.'''

    await call.answer(text=f'{emojize(":robot:")} Это просто заглушка...')
    

def register_some_func_handlers():
    '''Фукнция регистрации обработчиков для дополнительного функционала'''

    DP.register_callback_query_handler(plug_for_keyboard,
                                       callback_for_next_or_prev_button.filter(flag='plug'))
