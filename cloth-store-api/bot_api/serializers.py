from rest_framework import serializers

from bot_api.models import Categories, Items, OrderBasket, Order, OrderArchive, BotUsers


class CategoriesSerializer(serializers.ModelSerializer):
    '''Сериалайзер для категорий товаров'''

    class Meta:
        model = Categories
        fields = ['id', 'category_name']


class ItemsSerializer(serializers.ModelSerializer):
    '''Сериалайзер для товаров'''

    class Meta:
        model = Items
        fields = '__all__'


class OrderBasketSerializer(serializers.ModelSerializer):
    '''Сериалайзер для товаров из корзины'''

    class Meta:
        model = OrderBasket
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    '''Сериалайзер для заказов'''

    class Meta:
        model = Order
        fields = '__all__'


class OrderArchiveSerializer(serializers.ModelSerializer):
    '''Сериалайзер для архива заказов'''

    class Meta:
        model = OrderArchive
        fields = '__all__'


class BotUsersSerializer(serializers.ModelSerializer):
    '''Сериалайзер для пользователей бота'''

    class Meta:
        model = BotUsers
        fields = '__all__'
