from aiogram.types import MediaGroup
from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize

from another.request_to_API import get_items_categories, get_items_list
from keyboards.callback_data_bot import callback_for_next_or_prev_button, callback_for_category, \
    callback_back_to_categories, callback_for_headpage_inline_keyboard
from keyboards.inline_keyboard import category_item_formation_keyboard, items_list_formation_keyboard, \
    item_detail_formation_inline, pagination_between_items_formation_inline
from settings.config import DP, BOT, MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET


async def choose_goods(call: CallbackQuery):
    """Функция обработки нажатия на инлайн кнопку выбора товара."""

    await call.answer(f'{emojize(":robot:")} Работаю с сервером...')
    response = await get_items_categories()
    inline_keyboard_with_categories = category_item_formation_keyboard(response_data=response,
                                                                       message_id=call.message.message_id)

    user_messages_in_dict = MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.get(call.message.chat.id)
    if isinstance(user_messages_in_dict, dict):
        for i_key, i_value in user_messages_in_dict.items():
            if i_key == 'pagination_message':
                await call.message.edit_text(
                    text=f'🔻Выбери, что хочешь',
                    reply_markup=inline_keyboard_with_categories)
                continue
            for j_elem in i_value:
                await BOT.delete_message(chat_id=call.message.chat.id, message_id=j_elem)
        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.pop(call.from_user.id)

    else:
        await call.message.edit_text(
            text=f'{emojize(":backhand_index_pointing_down_medium_skin_tone:")} Выберите '
                 f'категорию товара',
            reply_markup=inline_keyboard_with_categories)


async def detail_goods_list_by_category(call: CallbackQuery, callback_data: dict):
    '''Отображение детальной информации о товарах в выбранной категории.'''

    await call.message.delete()  # Удаляем ранее отправленное сообщение в чате пользователя
    await call.answer(text=f'{emojize(":robot:")} Получаю список товаров у сервера...')
    response = await get_items_list(items_category_id=callback_data['category_id'])
    result_data = response.get('results')

    # Инициация словаря для хранения сообщений с товарами
    MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id] = dict()

    for i_item in result_data:
        if i_item['number_of_items'] < 1:  # Если товар отсутствует на складе, то не отображаем.
            continue
        items_id = i_item.get('id')
        items_name = i_item.get('items_name')
        description = i_item.get('description')
        price = i_item.get('price')
        clothes_size = i_item.get('clothes_size')
        image_for_items_id = i_item.get('image_for_items_id').split()

        # Отправляет фото, как медиа группу
        album = MediaGroup()
        for i_image_id in image_for_items_id:
            album.attach_photo(i_image_id)
        photo_message = await BOT.send_media_group(
            chat_id=call.message.chat.id,
            media=album
        )

        # Отправляем описание товара с кнопками
        inline_keyboard = item_detail_formation_inline(
            category_id=callback_data['category_id'],
            item_id=items_id,
        )
        item_message = await BOT.send_message(
            chat_id=call.message.chat.id,
            text=f'Название товара: {items_name}\n'
                 f'Описание товара: {description}\n'
                 f'Цена: {round(price, 2)} руб.\n'
                 f'Доступные размеры: {clothes_size}\n\n',
            reply_markup=inline_keyboard
        )

        # Абзац ниже для добавления id сообщений одного товара в словарь хранения
        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id][f'item_{items_id}'] = [item_message.message_id]
        for i_photo_msg in photo_message:
            MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id][f'item_{items_id}'].append(
                i_photo_msg.message_id)

    # Присылаем кнопки навигации
    pagination_inline_keyboard = pagination_between_items_formation_inline(response_data=response)
    pagination_message = await call.message.answer(
        text=f'{emojize("◀")} Кнопки навигации между товарами {emojize("▶")}',
        reply_markup=pagination_inline_keyboard
        )
    MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id]['pagination_message'] = pagination_message.message_id


''' ОБРАБОТЧИКИ КНОПОК НАВИГАЦИИ '''


async def pagination_step_for_items_categories(call: CallbackQuery, callback_data: dict):
    """Обработчик для пролистывание категорий товаров."""

    await call.answer(text=f'{emojize(":robot:")} Перелистываю страницу категорий...')
    pagination_step = callback_data.get('pagination_step')
    response = await get_items_categories(pagination_part_of_link=pagination_step)
    inline_keyboard = category_item_formation_keyboard(response_data=response, message_id=call.message.message_id)
    await call.message.edit_text(text=f'{emojize(":robot:")}Список категорий товаров.', reply_markup=inline_keyboard)


async def pagination_step_for_items_list(call: CallbackQuery, callback_data: dict):
    '''Обработчик для пролистывания категорий товаров.'''

    await call.answer(text=f'{emojize(":robot:")} Перелистываю страницу товаров...')
    pagination_step = callback_data['pagination_step']
    response = await get_items_list(pagination_part_of_link=pagination_step)

    result_data = response.get('results')

    # Удаляем сообщения с товарами
    user_messages_in_dict = MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.get(call.from_user.id)
    for i_key, i_value in user_messages_in_dict.items():
        if i_key == 'pagination_message':
            await BOT.delete_message(chat_id=call.message.chat.id, message_id=i_value)
            continue
        for j_elem in i_value:
            await BOT.delete_message(chat_id=call.message.chat.id, message_id=j_elem)
    MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET.pop(call.from_user.id)

    MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id] = dict()

    for i_item in result_data:
        if i_item['number_of_items'] < 1:  # Если товар отсутствует на складе, то не отображаем.
            continue
        items_id = i_item.get('id')
        items_name = i_item.get('items_name')
        description = i_item.get('description')
        price = i_item.get('price')
        clothes_size = i_item.get('clothes_size')
        image_for_items_id = i_item.get('image_for_items_id').split()

        # Отправляет фото, как медиа группу
        album = MediaGroup()
        for i_image_id in image_for_items_id:
            album.attach_photo(i_image_id)
        photo_message = await BOT.send_media_group(
            chat_id=call.message.chat.id,
            media=album
        )

        # Отправляем описание товара с кнопками
        inline_keyboard = item_detail_formation_inline(
            category_id=i_item.get('items_category'),
            item_id=items_id,
        )
        item_message = await BOT.send_message(
            chat_id=call.message.chat.id,
            text=f'Название товара: {items_name}\n'
                 f'Описание товара: {description}\n'
                 f'Цена: {round(price, 2)} руб.\n'
                 f'Доступные размеры: {clothes_size}\n\n',
            reply_markup=inline_keyboard
        )

        # Абзац ниже для добавления id сообщений одного товара в словарь хранения
        MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id][f'item_{items_id}'] = [item_message.message_id]
        for i_photo_msg in photo_message:
            MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id][f'item_{items_id}'].append(
                i_photo_msg.message_id)

    # Присылаем кнопки навигации
    pagination_inline_keyboard = pagination_between_items_formation_inline(response_data=response)
    pagination_message = await call.message.answer(
        text=f'{emojize("◀")} Кнопки навигации между товарами {emojize("▶")}',
        reply_markup=pagination_inline_keyboard
    )
    MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET[call.message.chat.id]['pagination_message'] = pagination_message.message_id


''' РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ '''


def register_items_menu_handlers():
    # новый функционал
    DP.register_callback_query_handler(choose_goods, callback_for_headpage_inline_keyboard.filter(flag='choose_goods'))
    DP.register_callback_query_handler(detail_goods_list_by_category,
                                       callback_for_category.filter(flag='category_for_items'))
    DP.register_callback_query_handler(pagination_step_for_items_categories,
                                       callback_for_next_or_prev_button.filter(flag='pagination_categories'))
    DP.register_callback_query_handler(choose_goods,
                                       callback_back_to_categories.filter(flag='back_to_categories'))
    DP.register_callback_query_handler(pagination_step_for_items_list,
                                       callback_for_next_or_prev_button.filter(flag='pagination_items'))
