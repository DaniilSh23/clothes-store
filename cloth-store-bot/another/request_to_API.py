import aiohttp
from loguru import logger
from settings.config import ITEMS_CATEGORIES_API_URL, ITEMS_LST_API_URL, ITEMS_DETAIL_API_URL, \
    ADD_ITEMS_IN_BASKET_API_URL, BASKET_API_URL, REMOVE_ITEMS_FROM_BASKET_API_URL, CLEAR_BASKET_API_URL, ORDERS_API_URL, \
    REMOVE_ORDER_API_URL, PAY_ORDER_INFO, ORDER_ARCHIVE, BOT_USER


@logger.catch
async def get_items_categories(pagination_part_of_link=None):
    '''Запрос для получения списка всех категорий товаров'''

    if pagination_part_of_link:
        req_link = ''.join([ITEMS_CATEGORIES_API_URL, pagination_part_of_link])
    else:
        req_link = ITEMS_CATEGORIES_API_URL

    # создаём клиент сессии
    async with aiohttp.ClientSession() as session:
        # выполняем GET запрос по указанному в константе адресу
        async with session.get(req_link) as response:
            # ждём выполнения корутины ответа и формируем из ответа json
            return await response.json()


@logger.catch
async def get_items_list(items_category_id=None, pagination_part_of_link=None):
    '''Запрос для получения списка товаров, согласно выбранной категории'''

    if pagination_part_of_link:
        req_link = ''.join([ITEMS_LST_API_URL, pagination_part_of_link])
    elif items_category_id:
        req_link = ''.join([ITEMS_LST_API_URL, f'?items_category_id={items_category_id}'])

    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            response = await response.json()
            return response


@logger.catch
async def get_item_detail_info(item_id):
    '''Запрос для получения детальной информации о товаре.'''

    req_link = ''.join([ITEMS_DETAIL_API_URL, item_id])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            response = await response.json()
            return response


@logger.catch
async def add_item_in_basket(user_tlg_id, item_id):
    '''Запрос для внесения товара в список корзины пользователя или повышения числа товаров.'''

    req_link = ''.join([ADD_ITEMS_IN_BASKET_API_URL, f'?user_tlg_id={user_tlg_id}&item_id={item_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            # работаем с объектом ответа
            async with response:
                # если статус 204(No Content) - выходим
                if response.status == 204:
                    return response.status
                else:
                    return await response.json()


@logger.catch
async def remove_item_from_basket(user_tlg_id, item_id):
    '''Запрос для удаления товара из корзины, либо уменьшение его количества.'''

    req_link = ''.join([REMOVE_ITEMS_FROM_BASKET_API_URL, f'?user_tlg_id={user_tlg_id}&item_id={item_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            async with response:
                if response.status == 204:
                    return response.status
                else:
                    return await response.json()


@logger.catch
async def get_user_basket(user_tlg_id, items_id=None):
    '''Запрос для получения товаров в корзине пользователя.'''

    req_link = ''.join([BASKET_API_URL, f'?user_tlg_id={user_tlg_id}'])
    if items_id:
        req_link = ''.join([req_link, f'&items_id={items_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            response = await response.json()
            return response


@logger.catch
async def clear_basket(user_tlg_id):
    '''Запрос для очистки корзины пользователя'''

    req_link = ''.join([CLEAR_BASKET_API_URL, f'?user_tlg_id={user_tlg_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            async with response:
                return response.status


@logger.catch
async def get_info_about_orders(user_tlg_id=None, order_id=None):
    '''Запрос для получения заказов.'''

    if user_tlg_id:
        req_link = ''.join([ORDERS_API_URL, f'?user_tlg_id={user_tlg_id}'])
    elif order_id:
        req_link = ''.join([ORDERS_API_URL, f'?order_id={order_id}'])
    elif not user_tlg_id and not order_id:
        req_link = ORDERS_API_URL
    else:
        raise Exception('Не переданы параметры для запроса.')

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(req_link) as response:
                async with response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 400:
                        return 400
    except Exception as error:
        logger.info(f'Запрос к API не удался. {error}')


@logger.catch
async def req_for_remove_order(order_id):
    '''Запрос для удаления заказа.'''

    req_link = ''.join([REMOVE_ORDER_API_URL, f'?id={order_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            async with response:
                if response.status == 200:
                    return 200
                else:
                    return 400


@logger.catch
async def post_req_for_add_order(order_data):
    '''POST запрос для внесения данных о заказе и получение ответа в виде этого же заказа.'''

    req_link = ''.join([ORDERS_API_URL])
    async with aiohttp.ClientSession() as session:
        async with session.post(url=req_link, data=order_data) as response:
            async with response:
                if response.status == 200:
                    return await response.json()
                else:
                    return 400


@logger.catch
async def post_req_for_add_pay_info_about_order(pay_order_data):
    '''POST запрос для создания в БД записи о данных оплаченного заказа.'''

    req_link = ''.join([PAY_ORDER_INFO])
    async with aiohttp.ClientSession() as session:
        async with session.post(url=req_link, data=pay_order_data) as response:
            async with response:
                if response.status == 200:
                    return True
                else:
                    return False


@logger.catch
async def post_req_for_add_order_to_archive(order_data):
    '''POST запрос для добавления заказа в архив.'''

    req_link = ''.join([ORDER_ARCHIVE])
    async with aiohttp.ClientSession() as session:
        async with session.post(url=req_link, data=order_data) as response:
            async with response:
                if response.status == 200:
                    return True
                else:
                    return False


@logger.catch
async def post_req_for_add_new_user(user_data):
    '''POST запрос для создания в БД записи о новом пользователе.'''

    req_link = ''.join([BOT_USER])
    async with aiohttp.ClientSession() as session:
        async with session.post(url=req_link, data=user_data) as response:
            async with response:
                if response.status == 200:
                    return True
                else:
                    return False


@logger.catch
async def get_user_info(user_id):
    '''POST запрос для создания в БД записи о новом пользователе.'''

    req_link = ''.join([BOT_USER, f"?user_id={user_id}"])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            async with response:
                if response.status == 200:
                    return await response.json()
                else:
                    return False
