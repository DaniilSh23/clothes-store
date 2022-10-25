from aiogram.utils.callback_data import CallbackData


# задаём передаваемые в кнопку параметры
callback_for_next_or_prev_button = CallbackData('@', 'pagination_step', 'flag')
callback_for_category = CallbackData('@', 'category_id', 'flag')
callback_for_items_by_category = CallbackData('@', 'item_id', 'message_id', 'flag')
callback_for_minus_plus_button = CallbackData('@', 'item_id', 'message_id', 'chat_id', 'user_tlg_id', 'req_flag', 'handler_flag')
callback_for_basket_and_order = CallbackData('@', 'user_tlg_id', 'flag')
callback_for_add_item_to_basket = CallbackData('@', 'item_id', 'category_id', 'flag')
callback_back_to_categories = CallbackData('@', 'flag')
callback_for_stuff = CallbackData('@', 'flag', 'order_id', 'chat_id', 'message_id')
callback_for_admins_orders_lst = CallbackData('@', 'flag')

# новенькое чисто под инлайн
callback_for_headpage = CallbackData('@', 'flag')
callback_for_headpage_inline_keyboard = CallbackData('@', 'flag')
callback_for_make_order = CallbackData('@', 'flag')
callback_for_basket = CallbackData('@', 'flag')
callback_for_accept_order = CallbackData('@', 'flag', 'user_tlg_id')
callback_for_orders_lst = CallbackData('@', 'flag', 'order_id', 'chat_id', 'message_id')
