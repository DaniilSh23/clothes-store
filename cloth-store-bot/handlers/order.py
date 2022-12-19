from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ParseMode
from aiogram.utils.emoji import emojize

from another.request_to_API import get_info_about_orders, req_for_remove_order, get_user_basket, post_req_for_add_order, \
    clear_basket, post_req_for_add_new_user
from keyboards.callback_data_bot import callback_for_orders_lst, callback_for_accept_order, \
    callback_for_headpage_inline_keyboard
from keyboards.common_keyboards import STAFF_REACTION, INLINE_KEYBOARD_BUTTON_HEADPAGE
from keyboards.inline_keyboard import order_formation_inline, stuff_formation_order_complete_inline
from settings.config import DP, BOT, STAFF_ID, MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET, KEYBOARD


async def my_order(call: CallbackQuery):
    """Обработчик для нажатия кнопки МОЙ ЗАКАЗ."""

    await call.message.edit_text(text=f'🗒Заказы\n\n'
                                      f'Для оформления, переходи в раздел "🛒Оформить заказ"',
                                 reply_markup=INLINE_KEYBOARD_BUTTON_HEADPAGE)
    user_tlg_id = call.from_user.id
    response = await get_info_about_orders(user_tlg_id)
    if response == 400:
        await call.answer(text=f'{emojize(":robot:")} Не удалось выполнить запрос к серверу...\n'
                               f'Мы разберёмся и скоро всё починим.',
                          show_alert=True)
    else:
        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id] = []
        for i_order in response:
            order_id = i_order.get('id')
            if i_order.get('pay_status'):
                pay_status = 'Оплачен'
            else:
                pay_status = 'НЕ оплачен'
            if i_order.get('execution_status'):
                execution_status = 'Готов'
            else:
                execution_status = 'НЕ готов'
            order_items = i_order.get('order_items').split('\n')
            result_orders_price = i_order.get('result_orders_price')
            text_for_message = f'<b><ins>{emojize(":receipt:")}Номер заказа: <tg-spoiler>{order_id}</tg-spoiler></ins></b>\n\n' \
                               f'<b>Cостав заказа:</b> \n'
            other_text = f'<b>\n{emojize(":money_with_wings:")}Итоговая цена заказа:</b> <tg-spoiler>{result_orders_price}</tg-spoiler> руб.\n\n' \
                         f'<b>Cтатус оплаты:</b> {pay_status}\n' \
                         f'<b>Статус выполнения:</b> {execution_status}\n\n' \
                         f'<b>{emojize(":mobile_phone:")}Контактный телефон:</b> {i_order.get("contact_telephone")}\n' \
                         f'<b>{emojize(":cityscape_at_dusk:")}Адрес доставки:</b> {i_order.get("delivery_address")}' \
                         f'<b>{emojize(":coat:")}Предпочитаемые размеры:</b> {i_order.get("sizes_for_clothes")}'

            for i_item in order_items:
                text_for_message = ''.join([text_for_message, i_item, '\n'])
            text_for_message = ''.join([text_for_message, other_text])
            i_message = await call.message.answer(text=text_for_message)
            chat_id = i_message.chat.id
            message_id = call.message.message_id
            inline_keyboard = order_formation_inline(order_id, chat_id, message_id)
            await i_message.edit_text(text=text_for_message, reply_markup=inline_keyboard)
            MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id].append(i_message.message_id)


async def remove_order(call: CallbackQuery, callback_data: dict):
    '''Обработчик для удаления заказа из БД.'''

    await call.answer(text=f'{emojize(":robot:")} Выполняю запрос к серверу для удаления заказа...')
    order_id = callback_data['order_id']
    response = await req_for_remove_order(order_id=order_id)
    if response == 200:
        await call.message.edit_text(text=f'Заказ № {order_id} был отменён.')
        # Отправляем уведомление об удалении персоналу
        for i_member in STAFF_ID:
            await BOT.send_message(chat_id=i_member, text=f'Пользователь отменил заказ № {order_id}',
                                   reply_markup=STAFF_REACTION)
    elif response == 400:
        await call.answer(text=f'{emojize(":robot:")}Запрос к серверу не удался. \nЗаказ не был удалён.',
                          show_alert=True)


async def add_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Обработчик для добавления нового заказа."""

    user = callback_data.get('user_tlg_id')
    user_tlg_name = call.from_user.username
    state_data = await state.get_data()
    client_name_data = state_data.get('your_name')
    phone_number_data = state_data.get('phone_number')
    delivery_address_data = state_data.get('delivery_address')
    sizes_for_clothes = state_data.get('your_size')

    response_basket = await get_user_basket(user_tlg_id=user)
    order_items = ''
    result_price = 0
    for i_item in response_basket:
        items_name = i_item[1]
        price = i_item[2]
        items_number_in_basket = i_item[3]

        result_price += price
        order_items = ''.join([
            order_items,
            f'Название товара: {items_name}\n',
            f'Количество: {items_number_in_basket} шт.\n',
            f'Цена за шт.: {price} руб.\n**********\n',
        ])

    # Формируем данные для запроса к модели пользователя.
    user_data = {
        'user_tlg_id': user,
        'user_tlg_name': user_tlg_name if user_tlg_name else None,
        'user_name': client_name_data,
        'last_shipping_address': delivery_address_data
    }
    response_user = await post_req_for_add_new_user(user_data=user_data)
    if not response_user:
        return await call.message.answer(text=f'{emojize(":robot:")} Ошибка сервера. Заказ не был создан...')

    # Формируем данные POST запроса для создания нового заказа.
    order_data = {
        'user': user,
        'order_items': order_items,
        'result_orders_price': result_price,
        'pay_status': False,
        'execution_status': False,
        'delivery_address': delivery_address_data,
        'contact_telephone': phone_number_data,
        'sizes_for_clothes': sizes_for_clothes,
    }
    response = await post_req_for_add_order(order_data)
    if response == 400:
        await call.message.answer(text=f'{emojize(":robot:")} Ошибка сервера. Заказ не был создан...')
    else:
        order_id = response['id']

        # формируем текст для сообщения
        if response.get('pay_status'):
            pay_status = 'Оплачен'
        else:
            pay_status = 'НЕ оплачен'
        if response.get('execution_status'):
            execution_status = 'Готов'
        else:
            execution_status = 'НЕ готов'
        order_items = response.get('order_items').split('\n')
        result_orders_price = response.get('result_orders_price')
        text_for_message = f'<b><ins>Номер заказа: {order_id}' \
                           f'</ins></b>\n<b>Cостав заказа:</b> \n'
        other_text = f'<b>\nИтоговая цена заказа:</b> {round(result_orders_price, 2)} руб.\n' \
                     f'<b>Cтатус оплаты:</b> {pay_status}\n' \
                     f'<b>Статус выполнения:</b> {execution_status}\n\n' \
                     f'<b>Заказ для:</b> <ins> {client_name_data}</ins>\n' \
                     f'<b>Адрес доставки:</b> {delivery_address_data}\n' \
                     f'<b>Номер телефона:</b> {phone_number_data}\n' \
                     f'<b>Номер телефона:</b> {sizes_for_clothes}'
        for i_item in order_items:
            text_for_message = ''.join([text_for_message, i_item, '\n'])
        text_for_message = ''.join([text_for_message, other_text])

        await clear_basket(user)

        # формируем инлайн клавиатуру и обновляем сообщение, чтобы её добавить
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        inline_keyboard = order_formation_inline(order_id, chat_id, message_id)
        await call.message.edit_text(text=text_for_message, reply_markup=inline_keyboard)
        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id] = [call.message.message_id]

        await BOT.send_message(chat_id=call.message.chat.id, text='Ваш заказ принят.\n'
                                                                  'Мы перезвоним Вам для подтверждения.',
                               reply_markup=INLINE_KEYBOARD_BUTTON_HEADPAGE)
        # Сбрасываем машину состояний для пользователя
        await state.reset_state(with_data=True)

        # Отправляем заказ персоналу
        for i_member in STAFF_ID:
            inline_keyboard = stuff_formation_order_complete_inline(order_id=order_id,
                                                                    chat_id=i_member, message_id=message_id)
            await BOT.send_message(chat_id=i_member, text=text_for_message, reply_markup=inline_keyboard)


def register_orders_handlers():
    DP.register_callback_query_handler(remove_order, callback_for_orders_lst.filter(flag='remove_order'))
    DP.register_callback_query_handler(add_order, callback_for_accept_order.filter(flag='yes'), state='*')
    DP.register_callback_query_handler(my_order, callback_for_headpage_inline_keyboard.filter(flag='my_order'))
