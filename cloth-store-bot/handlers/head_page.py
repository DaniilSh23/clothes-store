from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize

from another.request_to_API import post_req_for_add_new_user
from keyboards.callback_data_bot import callback_for_headpage_inline_keyboard
from keyboards.common_keyboards import HEAD_PAGE_INLINE_KEYBOARD, ADMINS_KEYBOARD, INLINE_KEYBOARD_BUTTON_HEADPAGE
from settings.config import DP, BOT, STAFF_ID, MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET, ADMINS_ID_LST


async def head_page(message: types.Message):
    '''Обработчик для главного меню бота, команда start, help'''

    user_data = {
        'user_tlg_id': message.from_user.id,
        'user_tlg_name': message.from_user.username
    }
    if message.from_user.first_name:
        user_name = message.from_user.first_name
        user_data['user_name'] = user_name
    response = await post_req_for_add_new_user(user_data)
    if response:
        text_for_message = emojize('🥷 Приветствую тебя в нашем Concept Store.  '
                                   'Индивидуальность - наша религия. HD - наш образ мыслей и стиль жизнь. '
                                   'Корпоративный цвет - черный.\n\n'
                                   'Здесь ты можешь найти одежду с принтами на тему HD или реализовать свою идею.\n'
                                   '🔻Каталог товаров🔻\n'
                                   '🗒Мои заказы\n'
                                   '🛒Корзина\n'
                                   '💬Обратная связь\n\n')
        await message.answer(
            text=text_for_message,
            reply_markup=HEAD_PAGE_INLINE_KEYBOARD
        )
    else:
        await message.answer(
            emojize(':robot: У бота что-то барохлит...:('
                    '\n:construction_worker: Мы уже разбираемся, '
                    'скоро он будет как новенький.:OK_hand:'))


async def return_to_head_page(call: CallbackQuery):
    '''Функция обработки возврата пользователя к главной странице'''

    await call.answer(f'{emojize(":robot:")} Возвращаемся к главному меню...')

    # удаляем в диалоге с ботом сообщения с товарами
    user_messages_in_dict = MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.get(call.from_user.id)
    if user_messages_in_dict and isinstance(user_messages_in_dict, list):
        for i_message_id in user_messages_in_dict:
            await BOT.delete_message(chat_id=call.from_user.id, message_id=i_message_id)
        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.pop(call.from_user.id)
        await call.message.delete()

    elif user_messages_in_dict and isinstance(user_messages_in_dict, dict):
        for i_key, i_value in user_messages_in_dict.items():
            if i_key == 'pagination_message':
                await BOT.delete_message(chat_id=call.message.chat.id, message_id=i_value)
                continue
            for j_elem in i_value:
                await BOT.delete_message(chat_id=call.message.chat.id, message_id=j_elem)
        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.pop(call.from_user.id)

    else:
        await BOT.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    # Основной функционал обработчика
    text_for_message = emojize(f'🥷ты вернулся в главное меню')
    new_message = await BOT.send_message(
        chat_id=call.message.chat.id,
        text=text_for_message,
        reply_markup=HEAD_PAGE_INLINE_KEYBOARD
    )

    if call.from_user.id in STAFF_ID:
        await new_message.edit_text(text=f'Вы администратор, для вас пару кнопок вдовесок', reply_markup=ADMINS_KEYBOARD)


async def send_media_id(message: types.Message):
    '''Обработчик для отправки ID присланного боту файла'''
    print(message)
    if message.from_user.id in ADMINS_ID_LST:
        await BOT.send_message(
            chat_id=message.from_user.id,
            text=f'{message.photo[-1].file_id}'
        )
    # await BOT.send_message(
    #     chat_id=message.from_user.id,
    #     text=f'ID файла: {message.photo[-1].file_id}'
    # )


async def about_store(call: CallbackQuery):
    """Обработчик для раздела с информацией о магазине."""

    text_about_cafe = f'<b>HDmerch Concept Store</b>\n\n' \
                      f'+7 966 070 70 79 Арунима\n\n' \
                      f'📌Как работаем:\n' \
                      f'- Ты оформляешь заказ в этом боте\n' \
                      f'- Мы связываемся с тобой, чтобы подтвердить заказ и обсудить все детали\n' \
                      f'- После разговора, ты оплачиваешь заказ\n' \
                      f'- Мы посылаем заказ (Boxberry, СДЭК, Почта России, по Москве - курьер)' \
                      f'- Высылаем тебе трек номер для отслеживания'
    await call.message.edit_text(text=text_about_cafe, reply_markup=INLINE_KEYBOARD_BUTTON_HEADPAGE)


async def size_table(call: CallbackQuery):
    '''Обработчик для кнопки таблицы размеров'''

    message_for_delete = MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.get(call.message.chat.id)
    if message_for_delete:
        for i_message in message_for_delete:
            await BOT.delete_message(
                chat_id=call.message.chat.id,
                message_id=i_message
            )
    await call.message.edit_text(
        text=f'{emojize(":white_exclamation_mark:")}Пожалуйста, ознакомься с таблицей размеров перед оформлением заказа.',
        reply_markup=INLINE_KEYBOARD_BUTTON_HEADPAGE
    )
    # AgACAgIAAxkBAAIFxWOgKu1ro2C8BZ1zdH-i5y0FPkE1AAK2xTEbfy0BSX8vfyHN6ReBAQADAgADeQADLAQ - это рабочий
    photo_message_1 = await BOT.send_photo(
        chat_id=call.message.chat.id,
        photo='AgACAgIAAxkBAAIFxWOgKu1ro2C8BZ1zdH-i5y0FPkE1AAK2xTEbfy0BSX8vfyHN6ReBAQADAgADeQADLAQ'
    )
    # AgACAgIAAxkBAAIFx2OgX7UnwXPqOiXeKaPeFch6Bf6HAAKmwzEbfy0JSZBiaa7KYBLJAQADAgADeQADLAQ - оригинальный
    # AgACAgIAAxkBAAI8jGOgo0oqDAABGrKRGohHw6AMImzKtAACfscxG4ohAUkUCTN3w0PwhgEAAwIAA3gAAywE - это тестовый
    photo_message_2 = await BOT.send_photo(
        chat_id=call.message.chat.id,
        photo='AgACAgIAAxkBAAIFx2OgX7UnwXPqOiXeKaPeFch6Bf6HAAKmwzEbfy0JSZBiaa7KYBLJAQADAgADeQADLAQ'
    )
    
    MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id] = [
        photo_message_1.message_id, 
        photo_message_2.message_id
        ]


def register_head_page_handlers():
    '''Функция для регистрации обработчиков'''

    DP.register_message_handler(head_page, Command(['start', 'home']))
    DP.register_callback_query_handler(return_to_head_page,
                                       callback_for_headpage_inline_keyboard.filter(flag='back_to_head_page'))
    DP.register_callback_query_handler(about_store, callback_for_headpage_inline_keyboard.filter(flag='info'))
    DP.register_message_handler(send_media_id, content_types=types.ContentTypes.PHOTO)
    DP.register_callback_query_handler(size_table, callback_for_headpage_inline_keyboard.filter(flag='size_table'))

