import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from emoji import emojize
import re

# токен выдается при регистрации приложения
TOKEN = os.environ.get('TOKEN', '5265303938:AAE1daGp-VJR0R15J9tHksR38hQlbCXMYdU')
PAY_TOKEN = os.environ.get('PAY_TOKEN', '1232131')

# Телеграм ID админов
ADMINS_ID_LST = [1978587604, 1112227426]
STAFF_ID = [1978587604]

# абсолютный путь до текущей директории этого файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COUNT = 0

# кнопки управления
KEYBOARD = {
    'CHOOSE_GOODS': emojize('🖤 Каталог товаров'),
    'INFO': emojize(':speech_balloon: Обратная связь'),
    'BASKET': emojize(':wastebasket: Корзина'),
    'MY_ORDER': emojize(':spiral_notepad: Мои заказы'),
    'HEAD_PAGE': emojize(":house_with_garden: Главная"),
    'MAKE_AN_ORDER': emojize('✅ ОФОРМИТЬ ЗАКАЗ'),
    'ORDER_COMPLETE': emojize('✅ ЗАКАЗ ВЫПОЛНЕН'),
    'X_ORDER': emojize('❌ ОТМЕНИТЬ ЗАКАЗ'),
    'X_BASKET': emojize('❌:wastebasket: ОЧИСТИТЬ'),
    'BACK_STEP_ITEM': emojize('◀️Назад'),
    'NEXT_STEP_ITEM': emojize('▶️Вперёд'),
    'BACK_STEP_CATEG': emojize('⏪Назад'),
    'NEXT_STEP_CATEG': emojize('⏩Вперёд'),
    'PLUS_ITEM': emojize(':plus:'),
    'MINUS_ITEM': emojize(':minus:'),
    'ORDER_GIVEN': emojize(':package:ЗАКАЗ ВЫПОЛНЕН'),
    'YES': emojize('✅'),
    'NO': emojize('❌ Нет'),
    'CANCEL_MAKE_ORDER': emojize('❌ Отменить оформление'),
    'SIZE_TABLE': emojize(':bar_chart:Таблица размеров'),
}

BUTTONS_FOR_CHOOSE_GOODS = {
    1: emojize(':backhand_index_pointing_right:'),
    2: emojize(':right_arrow:'),
    3: emojize('✅'),
    4: emojize(':handshake:'),
    5: emojize(':OK_hand:'),
    6: emojize(':thumbs_up:'),
}

# названия команд
COMMANDS = {
    'START': "start",
    'HELP': "help",
}

# URL адреса для запросов к АPI бота
DOMAIN_NAME = 'http://127.0.0.1:8000/'
ITEMS_CATEGORIES_API_URL = f'{DOMAIN_NAME}api/categories/'
ITEMS_LST_API_URL = f'{DOMAIN_NAME}api/items/'
BASKET_API_URL = f'{DOMAIN_NAME}api/basket/'
ADD_ITEMS_IN_BASKET_API_URL = f'{DOMAIN_NAME}api/add_items_in_basket/'
REMOVE_ITEMS_FROM_BASKET_API_URL = f'{DOMAIN_NAME}api/remove_items_from_basket/'
ORDERS_API_URL = f'{DOMAIN_NAME}api/orders/'
REMOVE_ORDER_API_URL = f'{DOMAIN_NAME}api/remove_order/'
CLEAR_BASKET_API_URL = f'{DOMAIN_NAME}api/clear_basket/'
ITEMS_DETAIL_API_URL = f'{DOMAIN_NAME}api/item_detail/?item_id='
PAY_ORDER_INFO = f'{DOMAIN_NAME}api/pay_order/'
ORDER_ARCHIVE = f'{DOMAIN_NAME}api/order_archive/'
ADMIN_PANEL = f'{DOMAIN_NAME}admin/'
BOT_USER = f'{DOMAIN_NAME}api/bot_user/'

# объекты: бот, диспатчер, сторэдж для машины состояний
BOT = Bot(token=TOKEN, parse_mode='HTML')
STORAGE = MemoryStorage()
DP = Dispatcher(BOT, storage=STORAGE)

# регулярные выражения для бота
# RE_CATEGORY_LINK_PATTERN = re.compile(r'\?\w*\S\w*')
RE_CATEGORY_LINK_PATTERN = re.compile(r'\?.*')

# # Адрес магазина.
# STORE_ADDRESS = f'Адрес магазина: город Севастополь, ул. Какая-либо д.23, телефон: +7 978 777 23 32'

# Словарь для хранения информации о id сообщений, которые были отправлены в корзине пользователя, в качестве товара
MESSAGES_ID_FOR_ITEMS_IN_USERS_BASKET = dict()
