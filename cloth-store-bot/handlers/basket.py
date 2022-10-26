from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize

from another.request_to_API import add_item_in_basket, get_user_basket, \
    remove_item_from_basket, clear_basket
from keyboards.callback_data_bot import callback_for_add_item_to_basket, callback_for_minus_plus_button, \
    callback_for_headpage_inline_keyboard, callback_for_basket
from keyboards.common_keyboards import INLINE_KEYBOARD_IN_BASKET, HEAD_PAGE_INLINE_KEYBOARD, \
    INLINE_KEYBOARD_WTH_HEADPAGE_AND_BASKET_BUTTON
from keyboards.inline_keyboard import basket_formation_inline
from settings.config import DP, BOT, MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET


async def add_item_to_basket(call: CallbackQuery, callback_data: dict):
    """Обработчик для добавления товара в корзину."""

    await call.answer(text=f'{emojize(":robot:")} Добавляю товар в корзину.\nЗапрос к серверу...')
    item_id = callback_data.get('item_id')
    user_tlg_id = call.from_user.id
    await add_item_in_basket(user_tlg_id=user_tlg_id, item_id=item_id)

    text_for_message = f'✅Товар добавлен в корзину.\n\n' \
                       f'В корзине Вы можете:\n{emojize(":star:")}отредактировать количество\n' \
                       f'{emojize(":star:")}оформить заказ\n{emojize(":star:")}удалить позицию.'

    await BOT.edit_message_text(
        text=text_for_message,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=INLINE_KEYBOARD_WTH_HEADPAGE_AND_BASKET_BUTTON
    )

    # Абзац ниже для удаления сообщений c фото товара
    msg_to_change = MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id][f'item_{item_id}']
    for i_elem, i_msg_id in enumerate(msg_to_change):
        if i_elem != 0:
            await BOT.delete_message(chat_id=call.message.chat.id, message_id=i_msg_id)
    else:
        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id][f'item_{item_id}'] = msg_to_change[0:1]


async def you_are_in_basket(call: CallbackQuery):
    '''Обработчик для перехода в корзину.'''

    # Проверяем, что в корзине добавлены товары
    response_basket = await get_user_basket(user_tlg_id=call.from_user.id)
    if len(response_basket) == 0:
        await call.message.edit_text(
            text=f'{emojize(":wastebasket:")}Твоя корзина пуста...',
            reply_markup=HEAD_PAGE_INLINE_KEYBOARD
        )

    else:

        # Удаляем в диалоге с ботом сообщения с товарами
        user_messages_in_dict = MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.get(call.from_user.id)
        if user_messages_in_dict and isinstance(user_messages_in_dict, dict):
            for i_key, i_value in user_messages_in_dict.items():
                if i_key == 'pagination_message':
                    await BOT.edit_message_text(
                        text=f'{emojize(":robot:")} Корзина {emojize(":wastebasket:")}\n'
                             f'Выбранные Вами товары представлены ниже.\n'
                             f'Вы можете отредактировать их, если нужно, и оформить заказ.',
                        chat_id=call.message.chat.id,
                        message_id=i_value,
                        reply_markup=INLINE_KEYBOARD_IN_BASKET
                    )
                    continue
                for j_elem in i_value:
                    await BOT.delete_message(chat_id=call.message.chat.id, message_id=j_elem)
            MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.pop(call.from_user.id)

        # Основная логика обработчика
        else:
            await call.message.edit_text(f'{emojize(":robot:")} Корзина {emojize(":wastebasket:")}\n'
                                         f'Выбранные Вами товары представлены ниже.\n'
                                         f'Вы можете отредактировать их, если нужно, и оформить заказ.',
                                         reply_markup=INLINE_KEYBOARD_IN_BASKET)
        user_tlg_id = call.from_user.id
        chat_id = call.message.chat.id
        response = await get_user_basket(user_tlg_id)

        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id] = []
        for i_elem in response:
            item_id = i_elem[0]
            item_name = i_elem[1]
            items_numbers_in_basket = i_elem[3]
            total_price = round(i_elem[2] * items_numbers_in_basket, 2)
            text_for_message = f'{emojize(":large_blue_diamond:")}Название товара: {item_name}\n' \
                               f'{emojize(":large_orange_diamond:")}Количество: {items_numbers_in_basket} шт.\n' \
                               f'{emojize(":large_blue_diamond:")}Итоговая цена позиции: {total_price} руб.'
            i_message = await call.message.answer(text=text_for_message)
            inline_keyboard = basket_formation_inline(i_message.message_id, user_tlg_id, item_id,
                                                      items_numbers_in_basket,
                                                      chat_id)
            await i_message.edit_text(text=text_for_message, reply_markup=inline_keyboard)
            MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id].append(i_message.message_id)


async def change_items_in_basket(call: CallbackQuery, callback_data: dict):
    '''Обработчик для изменения количества товаров в корзине.'''

    await call.answer(text=f'{emojize(":robot:")} Редактирую корзину.\nЗапрос к серверу...')
    # сперва изменяем кол-во товаров в БД
    user_tlg_id = callback_data['user_tlg_id']
    item_id = callback_data['item_id']
    flag = callback_data['req_flag']
    chat_id = callback_data.get('chat_id')
    message_id = callback_data.get('message_id')
    if flag == 'plus':
        change_response = await add_item_in_basket(user_tlg_id, item_id)
        # если получили ответом статус==204, то выходим из функции
        if change_response == 204:
            await call.answer(text=f'{emojize(":robot:")}Товара закончился...', show_alert=True)
            return
    elif flag == 'minus':
        change_response = await remove_item_from_basket(user_tlg_id, item_id)
        # если получили ответом статус==204, то выходим из функции
        if change_response == 204:

            # удаляем из списка в словаре, где хранятся ID сообщений с товарами для пользователя ID данного сообщения
            if len(MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id]) == 1:
                MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id].clear()
            else:
                MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id].remove(message_id)

            # удаляем сообщение с товаром и информируем пользователя
            await BOT.delete_message(chat_id=chat_id, message_id=message_id)
            await call.answer(text=f'{emojize(":robot:")}Товар удалён из корзины...', show_alert=True)
            return

    # теперь делаем заново запрос на получение нужного товара из корзины
    result_response = await get_user_basket(user_tlg_id, item_id)
    items_numbers_in_basket = result_response[0][3]
    item_name = result_response[0][1]
    total_price = result_response[0][2] * items_numbers_in_basket
    text_for_message = f'{emojize(":bookmark:")}Название товара: {item_name}\n' \
                       f'{emojize(":input_numbers:")}Количество: {items_numbers_in_basket} шт.\n' \
                       f'{emojize(":money_with_wings:")}Итоговая цена позиции: {round(total_price, 2)} руб.'
    inline_keyboard = basket_formation_inline(message_id, user_tlg_id, item_id, items_numbers_in_basket, chat_id)
    await BOT.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=inline_keyboard,
                                text=text_for_message)


async def clear_the_basket(call: CallbackQuery):
    '''Обработчик для очистки корзины'''

    user_tlg_id = call.from_user.id
    response = await clear_basket(user_tlg_id)

    if response == 200:
        # удаляем в диалоге с ботом сообщения с товарами из корзины пользователя
        if MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.get(call.from_user.id):
            for i_message_id in MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id]:
                await BOT.delete_message(chat_id=call.from_user.id, message_id=i_message_id)
            MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.pop(call.from_user.id)

        text_for_message = f'{emojize(":robot:")}Ваша корзина очищена...\n' \
                           f'{emojize(":shopping_bags:")}Давайте добавим в неё что-нибудь.\n\n'
        await call.message.edit_text(text=text_for_message, reply_markup=HEAD_PAGE_INLINE_KEYBOARD)
    else:
        await call.message.answer(text=f'{emojize(":robot:")}Проблемы с сервером...Не удалось выполнить запрос.',
                                  reply_markup=HEAD_PAGE_INLINE_KEYBOARD)


def register_basket_handlers():
    '''Функция для регистрации обработчиков корзины товаров.'''

    DP.register_callback_query_handler(add_item_to_basket,
                                       callback_for_add_item_to_basket.filter(flag='add_item_to_basket_from_detail'))
    DP.register_callback_query_handler(you_are_in_basket,
                                       callback_for_headpage_inline_keyboard.filter(flag='go_to_basket'))
    DP.register_callback_query_handler(change_items_in_basket,
                                       callback_for_minus_plus_button.filter(handler_flag='change_in_basket'))
    DP.register_callback_query_handler(clear_the_basket, callback_for_basket.filter(flag='clear_the_basket'))
