from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize

from another.request_to_API import post_req_for_add_new_user
from keyboards.callback_data_bot import callback_for_headpage_inline_keyboard
from keyboards.common_keyboards import HEAD_PAGE_INLINE_KEYBOARD, ADMINS_KEYBOARD, INLINE_KEYBOARD_BUTTON_HEADPAGE
from settings.config import DP, BOT, STAFF_ID, MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET


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
        await message.answer(
            emojize(':waving_hand:Привет!\n\n :shopping_bags:Этот бот поможет быстро ознакомиться с '
                    'нашим ассортиментом и оформить заказ, не выходя из любимого мессенджера.\n\n'
                    'Вы можете добавить товар в корзину, оформить заказ и '
                    'получить с доставкой в руки.:handshake_light_skin_tone:\n\n'
                    'Это удобно, просто нажмите на кнопку "✅ Выбрать товар" :slightly_smiling_face:'),
            reply_markup=HEAD_PAGE_INLINE_KEYBOARD)
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
    text_for_message = emojize(f'{emojize(":house_with_garden:")} Вы вернулись к главному меню')
    new_message = await BOT.send_message(
        chat_id=call.message.chat.id,
        text=text_for_message,
        reply_markup=HEAD_PAGE_INLINE_KEYBOARD
    )

    if call.from_user.id in STAFF_ID:
        await new_message.edit_text(text=f'Вы администратор, для вас пару кнопок вдовесок', reply_markup=ADMINS_KEYBOARD)


async def send_media_id(message: types.Message):
    '''Обработчик для отправки ID присланного боту файла'''

    # if message.from_user.id in ADMINS_ID_LST:
    #     await BOT.send_message(
    #         chat_id=message.from_user.id,
    #         text=f'ID файла: {message.photo[-1].file_id}'
    #     )
    await BOT.send_message(
        chat_id=message.from_user.id,
        text=f'ID файла: {message.photo[-1].file_id}'
    )


async def about_store(call: CallbackQuery):
    """Обработчик для раздела с информацией о магазине."""

    text_about_cafe = f'{emojize(":department_store:")}<b><ins>HDmerch</ins></b>\n\n' \
                      f'{emojize(":four_o’clock:")}<ins>Режим работы:</ins> 08:00 - 20:30\n' \
                      f'{emojize(":telephone_receiver:")}<ins>Контактый телефон:</ins> +7 777-77-23\n\n' \
                      f'{emojize(":telephone_receiver:")}<ins>Как мы работаем:</ins>\n' \
                      f'{emojize(":keycap_1:")}Вы оформляете заказ.\n' \
                      f'{emojize(":keycap_2:")}Мы перезваниваем Вам, чтобы его подтвердить.\n' \
                      f'{emojize(":keycap_3:")}Доставляем Вам товар.\n' \
                      f'{emojize(":keycap_4:")}Вы производите оплату и остаётесь довольны, потому что это удобно.\n\n' \
                      f''
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
        text=f'{emojize(":white_exclamation_mark:")}Пожалуйста, ознакомьтесь с таблицей размеров перед оформлением заказа.',
        reply_markup=INLINE_KEYBOARD_BUTTON_HEADPAGE
    )
    photo_message = await BOT.send_photo(
        chat_id=call.message.chat.id,
        photo='AgACAgIAAxkBAAIjKmNW1hnKhxilPCFrdvoo2Wg_VH1cAALmwDEb_LyxSs6Nr-Qt_OTCAQADAgADeQADKgQ'
    )
    MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id] = [photo_message.message_id]


def register_head_page_handlers():
    '''Функция для регистрации обработчиков'''

    DP.register_message_handler(head_page, Command(['start', 'home']))
    DP.register_callback_query_handler(return_to_head_page,
                                       callback_for_headpage_inline_keyboard.filter(flag='back_to_head_page'))
    DP.register_callback_query_handler(about_store, callback_for_headpage_inline_keyboard.filter(flag='info'))
    DP.register_message_handler(send_media_id, content_types=types.ContentTypes.PHOTO)
    DP.register_callback_query_handler(size_table, callback_for_headpage_inline_keyboard.filter(flag='size_table'))

