from aiogram.dispatcher.filters.state import StatesGroup, State


class MakeOrderStates(StatesGroup):
    '''Класс для машины состояний при оформлении заказа.'''

    delivery_address = State()
    phone_number = State()
    your_name = State()
    your_size = State()

