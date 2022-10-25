import asyncio
from loguru import logger

from another.some_func import register_some_func_handlers
from handlers.basket import register_basket_handlers
from handlers.head_page import register_head_page_handlers
from handlers.items_menu import register_items_menu_handlers
from handlers.order import register_orders_handlers
from handlers.staff import register_staff_handlers
from handlers.steps_for_make_order import register_steps_for_make_order_handlers
from middlewares.throttling_middleware import ThrottlingMiddleware
from settings.config import BOT, DP


def register_all_middlewares():
    '''Функция для регистрации мидлов'''
    DP.middleware.setup(ThrottlingMiddleware())


def register_all_handlers():
    '''Функция для регистрации всех обработчиков'''
    logger.info('START register_all_handlers FUNC')
    register_head_page_handlers()
    register_items_menu_handlers()
    register_basket_handlers()
    register_orders_handlers()
    register_staff_handlers()
    register_steps_for_make_order_handlers()
    register_some_func_handlers()


@logger.catch
async def main():
    '''Функция запуска бота.'''
    logger.info('BOT IS READY TO LAUNCH!\nstarting the countdown...')

    logger.info('3... Config for launch')
    bot = BOT
    dp = DP

    # вызовем поочередно регистрацию мидлов, фильтров и обработчиков
    # для того, чтобы эти мидлы, фильтры и обработчики регистрировались
    # на нашего бота в функцю нужно передать инстанс диспатчера
    logger.info('2... Register middlewares, filter and handlers')
    register_all_middlewares()
    # register_all_filters(dp)
    register_all_handlers()

    # ну и пропишем запуск нашего бота.
    # ниже мы будем постоянно проверять обновления в боте
    try:
        logger.info('1... LAUNCH!')
        await dp.start_polling()
    finally:
        logger.info('Bot has landed...\nSTOP ENGINE!')
        # в случае каких-либо ошибок
        # закрываем соединение с нашим хранилищем (БД например)
        await dp.storage.close()
        # ждём пока хранилище закроется
        await dp.storage.wait_closed()
        # закрываем сессию бота
        await bot.session.close()

if __name__ == '__main__':
    try:
        # методу run передаём корутину функции
        asyncio.run(main())
    # KeyboardInterrupt - CTRL + C, в общем бот будет завершать работу при нажатии клавиш или выхода из системы
    except (KeyboardInterrupt, SystemExit):
        logger.error('BOT STOPPED with exception!')

