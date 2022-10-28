from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from emoji.core import emojize

from keyboards.callback_data_bot import callback_for_headpage_inline_keyboard, callback_for_make_order, \
    callback_for_basket, callback_for_admins_orders_lst, callback_for_headpage
from settings.config import KEYBOARD, ADMIN_PANEL

INLINE_KEYBOARD_IN_BASKET = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [
        InlineKeyboardButton(
            text=KEYBOARD['MAKE_AN_ORDER'],
            callback_data=callback_for_make_order.new(
                flag='first_step_for_make_order',
            )
        )
    ],
    [
        InlineKeyboardButton(
            text=KEYBOARD['HEAD_PAGE'],
            callback_data=callback_for_headpage_inline_keyboard.new(
                flag='back_to_head_page',
            )),
        InlineKeyboardButton(
            text=KEYBOARD['X_BASKET'],
            callback_data=callback_for_basket.new(
                flag='clear_the_basket',
            ))
    ],
])

SIZE_TABLE_BUTTON = InlineKeyboardButton(text=KEYBOARD['SIZE_TABLE'],
                                         callback_data=callback_for_headpage_inline_keyboard.new(
                                             flag='size_table'
                                         ))

INLINE_KEYBOARD_BUTTON_HEADPAGE = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    [
        InlineKeyboardButton(
            text=KEYBOARD['HEAD_PAGE'],
            callback_data=callback_for_headpage_inline_keyboard.new(
                flag='back_to_head_page',
            )),
    ],
])

HEAD_PAGE_INLINE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=KEYBOARD['CHOOSE_GOODS'],
                                 callback_data=callback_for_headpage_inline_keyboard.new(
                                     flag='choose_goods'
                                 ))
        ],
        [
            InlineKeyboardButton(text=KEYBOARD['MY_ORDER'],
                                 callback_data=callback_for_headpage_inline_keyboard.new(
                                     flag='my_order'
                                 )),
            InlineKeyboardButton(text=KEYBOARD['BASKET'],
                                 callback_data=callback_for_headpage_inline_keyboard.new(
                                     flag='go_to_basket'
                                 )),
        ],
        [
            InlineKeyboardButton(text=KEYBOARD['INFO'],
                                 callback_data=callback_for_headpage_inline_keyboard.new(
                                     flag='info'
                                 )),
        ]
    ]
)

ADMINS_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=KEYBOARD['CHOOSE_GOODS'],
                                 callback_data=callback_for_headpage_inline_keyboard.new(
                                     flag='choose_goods'
                                 ))
        ],
        [
            InlineKeyboardButton(text=KEYBOARD['MY_ORDER'],
                                 callback_data=callback_for_headpage_inline_keyboard.new(
                                     flag='my_order'
                                 )),
            InlineKeyboardButton(text=KEYBOARD['BASKET'],
                                 callback_data=callback_for_headpage_inline_keyboard.new(
                                     flag='go_to_basket'
                                 )),
        ],
        [
            InlineKeyboardButton(text=KEYBOARD['INFO'],
                                 callback_data=callback_for_headpage_inline_keyboard.new(
                                     flag='info'
                                 )),
        ],
        [
            InlineKeyboardButton(text='Админ панель', url=ADMIN_PANEL),
        ],
        [
            InlineKeyboardButton(text='Список заказов', callback_data=callback_for_admins_orders_lst.new(
                flag='orderslst'
            ))
        ]

    ]
)

CANCEL_ORDER_BUTTON = InlineKeyboardButton(text='❌', callback_data=callback_for_make_order.new(flag='cancel'))

STAFF_REACTION = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    [
        InlineKeyboardButton(
            text=f'{emojize(":fire:")}Спасибо, я проинформирован.',
            callback_data=callback_for_headpage.new(
                flag='back_to_head_page'
            )
        )
    ]])

INLINE_KEYBOARD_WTH_HEADPAGE_AND_BASKET_BUTTON = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [
        InlineKeyboardButton(
            text=KEYBOARD['BASKET'],
            callback_data=callback_for_headpage_inline_keyboard.new(
                flag='go_to_basket'
            )),
        InlineKeyboardButton(
            text=KEYBOARD['HEAD_PAGE'],
            callback_data=callback_for_headpage_inline_keyboard.new(
                flag='back_to_head_page',
            )),
    ]
])
