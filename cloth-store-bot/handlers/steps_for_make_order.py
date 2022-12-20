from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from emoji.core import emojize

from another.accept_order import check_and_accept_order
from keyboards.callback_data_bot import callback_for_make_order
from keyboards.common_keyboards import HEAD_PAGE_INLINE_KEYBOARD, CANCEL_ORDER_BUTTON, ADMINS_KEYBOARD
from keyboards.inline_keyboard import accept_order_inline_keyboard_formation
from settings.config import DP, BOT, MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET, STAFF_ID
from states.states import MakeOrderStates


async def first_step_for_make_order(call: CallbackQuery):
    """Первый шаг оформления заказа. Запрашиваем адрес доставки"""

    # если, находясь в корзине, бот не присылал сообщения с товарами, то вернёмся на главную
    if len(MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id]) == 0:
        await call.message.edit_text('Ваша корзина пуста...', reply_markup=HEAD_PAGE_INLINE_KEYBOARD)
    else:
        # удаляем в диалоге с ботом сообщения с товарами из корзины пользователя
        if MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.get(call.from_user.id):
            for i_message_id in MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.from_user.id]:
                await BOT.delete_message(chat_id=call.from_user.id, message_id=i_message_id)
            MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.pop(call.from_user.id)

        await call.answer(text=f'🥷 Приступаем к оформлению заказа...')
        await MakeOrderStates.delivery_address.set()
        await call.message.edit_text(
            text=f'🥷Оформляю заказ\n\n'
                 f'🔻Адрес доставки',
            reply_markup=InlineKeyboardMarkup(row_width=1).insert(CANCEL_ORDER_BUTTON)
        )


async def second_step_make_order(message: types.Message, state: FSMContext):
    '''Второй шаг оформления заказа. Запрашиваем номер телефона.'''

    await state.update_data(delivery_address=message.text)
    await MakeOrderStates.phone_number.set()
    await message.answer(text=f'🔻Твой контактный номер телефона',
                         reply_markup=InlineKeyboardMarkup(row_width=1).insert(CANCEL_ORDER_BUTTON))


async def third_step_make_order(message: types.Message, state: FSMContext):
    '''Третий шаг оформления заказа. Запрашиваем имя контактного лица.'''

    await state.update_data(phone_number=message.text)
    await MakeOrderStates.your_name.set()
    await message.answer(text=f'🔻Как к тебе можно обращаться?',
                         reply_markup=InlineKeyboardMarkup(row_width=1).insert(CANCEL_ORDER_BUTTON))


async def fourth_step_make_order(message: types.Message, state: FSMContext):
    '''Четвертый шаг оформления заказа. Запрашиваем предпочитаемый размер.'''

    await state.update_data(your_name=message.text)
    await MakeOrderStates.your_size.set()
    await message.answer(text=f'Твой предпочитаемый размер для товаров из заказа.\n\n'
                              f'Укажи в свободной форме.\n(Например: S, M, L, XL или 42-44 и т.д.)🔻',
                         reply_markup=InlineKeyboardMarkup(row_width=1).insert(CANCEL_ORDER_BUTTON))


async def fifth_step_make_order(message: types.Message, state: FSMContext):
    '''Четвертый шаг оформления заказа. Отправляем заказ на подтверждение пользователю.'''

    await state.update_data(your_size=message.text)
    state_data = await state.get_data()

    text_for_message = await check_and_accept_order(
        user_tlg_id=message.from_user.id,
        delivery_address_data=state_data.get('delivery_address'),
        phone_number_data=state_data.get('phone_number'),
        your_name_data=state_data.get('your_name'),
        your_size_data=state_data.get('your_size'),
    )

    inline_keyboard = accept_order_inline_keyboard_formation(user_tlg_id=message.from_user.id)
    await message.answer(text=text_for_message, reply_markup=inline_keyboard)


async def cancel_order(call: CallbackQuery, state: FSMContext):
    '''Обработчик для инлайн кнопки отмена оформления заказа.'''

    await call.answer(text=f'Ты отменил оформление заказа...{emojize(":face_with_rolling_eyes:")}', show_alert=True)
    await state.reset_state(with_data=True)
    await call.message.delete()

    this_message = await BOT.send_message(text=f'Ты перешёл к главному меню', reply_markup=HEAD_PAGE_INLINE_KEYBOARD, chat_id=call.message.chat.id)
    if call.from_user.id in STAFF_ID:
        await this_message.edit_text(text=f'Вы администратор, для вас пару кнопок в довесок',
                                     reply_markup=ADMINS_KEYBOARD)


def register_steps_for_make_order_handlers():
    '''Регистрация обработчиков для шагов оформления заказа.'''

    DP.register_callback_query_handler(first_step_for_make_order,
                                       callback_for_make_order.filter(flag='first_step_for_make_order'), state='*')
    DP.register_message_handler(second_step_make_order, state=MakeOrderStates.delivery_address)
    DP.register_message_handler(third_step_make_order, state=MakeOrderStates.phone_number)
    DP.register_message_handler(fourth_step_make_order, state=MakeOrderStates.your_name)
    DP.register_message_handler(fifth_step_make_order, state=MakeOrderStates.your_size)
    DP.register_callback_query_handler(cancel_order, callback_for_make_order.filter(flag='cancel'), state='*')
