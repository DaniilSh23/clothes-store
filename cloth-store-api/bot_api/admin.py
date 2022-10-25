from django.contrib import admin
from bot_api.models import Categories, Items, OrderBasket, Order, OrderArchive, BotUsers


class CategoriesAdmin(admin.ModelAdmin):
    '''Регистрация модели категорий товаров в админ панели'''
    list_display = ['id', 'category_name']
    list_display_links = ['id', 'category_name']


class ItemsAdmin(admin.ModelAdmin):
    '''Регистрация модели товаров в админ панели'''
    list_display = ['id', 'items_name', 'price', 'number_of_items', 'items_category']
    list_display_links = ['id', 'items_name', 'price', 'number_of_items', 'items_category']


class OrderBasketAdmin(admin.ModelAdmin):
    '''Регистрация модели товаров из корзины в админ панели'''
    list_display = ['id', 'items_id', 'items_number_in_basket', 'user']
    list_display_links = ['id', 'items_id', 'items_number_in_basket', 'user']


class OrderArchiveAdmin(admin.ModelAdmin):
    '''Регистрация модели архива заказов в админ панели.'''
    list_display = ['id', 'order_id_before_receiving', 'datetime', 'result_orders_price']
    list_display_links = ['id', 'order_id_before_receiving', 'datetime', 'result_orders_price']


class OrderAdmin(admin.ModelAdmin):
    '''Регистрация модели заказа в админ панели'''
    list_display = ['id', 'user', 'datetime', 'pay_status', 'execution_status', 'order_items', 'result_orders_price']
    list_display_links = ['id', 'user', 'datetime', 'pay_status', 'execution_status', 'order_items', 'result_orders_price']


class BotUsersAdmin(admin.ModelAdmin):
    '''Регистрация модели пользователя'''

    list_display = ['id', 'user_tlg_name', 'orders_numb']
    list_display_links = ['id', 'user_tlg_name', 'orders_numb']


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Items, ItemsAdmin)
admin.site.register(OrderBasket, OrderBasketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(BotUsers, BotUsersAdmin)
admin.site.register(OrderArchive, OrderArchiveAdmin)
