from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from bot_api.models import Categories, Items, OrderBasket, Order, OrderArchive, BotUsers
from bot_api.pagination import CategoryPagination
from bot_api.serializers import ItemsSerializer, CategoriesSerializer, OrderBasketSerializer, OrderSerializer, \
    OrderArchiveSerializer, BotUsersSerializer


# 1
class CategoryView(generics.ListAPIView):
    """Представление списка всех категорий"""

    serializer_class = CategoriesSerializer
    # выбор класса-пагинатора
    pagination_class = CategoryPagination   # Переопределённый мной класс пагинации для категорий товаров (по 4 на странице)

    def get_queryset(self):
        """
        Переопределённый метод из GenericAPIView для отбора нужных нам данных
        """
        # берём все данные из таблицы БД
        queryset = Categories.objects.all()
        return queryset


# 2
class ItemsListView(generics.ListAPIView):
    """Представление списка всех товаров для конкретной категории"""

    serializer_class = ItemsSerializer
    # выбор класса-пагинатора
    pagination_class = PageNumberPagination  # кажется, его необязательно прописывать

    def get_queryset(self):
        """
        Переопределённый метод из GenericAPIView для отбора нужных нам данных
        """

        # берём данные по ключу items_category из запроса пользователя
        items_category_id = self.request.query_params.get('items_category_id')
        # проверяем есть ли данные по такому ключу в запросе пользователя
        if items_category_id:
            # отбираем те записи БД, у которых поле items_category == значению из запроса пользователя
            queryset = Items.objects.filter(items_category=items_category_id)
        else:
            queryset = Items.objects.all()
        return queryset


# 3
class OrderBasketView(APIView):
    """Представление списка товаров из корзины пользователя.
    В запросе требуется укзать /?user_tlg_id=...
    И при необходимости получить конкретный товар ...&items_id="""

    pagination_class = PageNumberPagination

    def get(self, request, format=None):
        user_tlg_id = request.query_params.get('user_tlg_id')
        items_id = request.query_params.get('items_id')
        user = BotUsers.objects.get(user_tlg_id=user_tlg_id)
        if items_id:
            user_basket = OrderBasket.objects.filter(user=user, items_id__pk=items_id).select_related('items_id')
        else:
            user_basket = OrderBasket.objects.filter(user=user).select_related('items_id')
        user_basket = user_basket.values_list(
            'items_id',
            'items_id__items_name',
            'items_id__price',
            'items_number_in_basket',
            'items_id__number_of_items',
        )
        return Response(user_basket, status.HTTP_200_OK)


# 4
class AddItemToBasket(APIView):
    """Представление для добавления товара в корзину"""

    def get(self, request, format=None):
        # получение параметров запроса
        user_tlg_id = request.query_params.get('user_tlg_id')
        item_id = request.query_params.get('item_id')
        user = BotUsers.objects.get(user_tlg_id=user_tlg_id)
        # берём объект товара
        item = Items.objects.get(pk=item_id)
        if item.number_of_items != 0:
            item.number_of_items -= 1
            item.save()
        else:
            return Response({'no_items': 'Нет в наличии'}, status.HTTP_204_NO_CONTENT)
        # берём из БД или создаём новую запись в корзине
        basket_object = OrderBasket.objects.get_or_create(
            items_id=item,
            user=user
        )
        # проверяем, что запись в БД не была создана
        if not basket_object[1]:
            # добавляем +1 к количеству товаров и сохраняем изменения в БД
            basket_object[0].items_number_in_basket += 1
            basket_object[0].save()
        result_object = OrderBasketSerializer(basket_object[0], many=False).data
        return Response(result_object, status.HTTP_201_CREATED)


# 5
class RemoveItemToBasket(APIView):
    """Представление для удаления товара из корзины"""

    def get(self, request, format=None):
        # получение параметров запроса
        user_tlg_id = request.query_params.get('user_tlg_id')
        item_id = request.query_params.get('item_id')
        user = BotUsers.objects.get(user_tlg_id=user_tlg_id)

        # берём объект товара
        item = Items.objects.get(pk=item_id)
        # добавляем +1 к общему числу товаров на "складе"
        item.number_of_items += 1
        item.save()

        # берём запись из корзины
        basket_object = OrderBasket.objects.get(
            items_id=item,
            user=user
        )
        # отнимаем от количества товаров 1
        basket_object.items_number_in_basket -= 1
        # если товаров меньше 1, то удаляем запись из БД корзины товаров
        if basket_object.items_number_in_basket < 1:
            basket_object.delete()
            result_object = {'deleted_from_basket': 'удалено из корзины'}
            return Response(result_object, status.HTTP_204_NO_CONTENT)
        else:
            # иначе сохраняем изменения
            basket_object.save()
            result_object = OrderBasketSerializer(basket_object, many=False).data
            return Response(result_object, status.HTTP_200_OK)


# 6
class OrdersView(APIView):
    """Представление для добавления или обновления записей о заказах."""

    def get(self, request, format=None):
        """Получение списка заказов. Для конкретного пользователя передать /?user_tlg_id=...."""

        user_tlg_id = request.query_params.get('user_tlg_id')
        order_id = request.query_params.get('order_id')

        if user_tlg_id:
            user = BotUsers.objects.get(user_tlg_id=user_tlg_id)
            orders = Order.objects.filter(user=user)
            orders_serializer = OrderSerializer(orders, many=True).data
            return Response(orders_serializer, status.HTTP_200_OK)

        elif order_id:
            order = Order.objects.get(id=order_id)
            orders_serializer = OrderSerializer(order, many=False).data
            return Response(orders_serializer, status.HTTP_200_OK)

        elif not user_tlg_id and not order_id:
            orders = Order.objects.all()
            orders_serializer = OrderSerializer(orders, many=True).data
            return Response(orders_serializer, status.HTTP_200_OK)

        return Response(status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        orders_id = request.data.get('id')
        serializer = OrderSerializer(data=request.data)
        user = BotUsers.objects.get(user_tlg_id=request.data.get('user'))
        order_object = Order.objects.update_or_create(id=orders_id, defaults={
            'user': user,
            'pay_status': request.data.get('pay_status'),
            'execution_status': request.data.get('execution_status'),
            'order_items': request.data.get('order_items'),
            'result_orders_price': request.data.get('result_orders_price'),
            'delivery_address': request.data.get('delivery_address'),
            'contact_telephone': request.data.get('contact_telephone'),
            'sizes_for_clothes': request.data.get('sizes_for_clothes')
        })

            # "pay_status": false,
            # "execution_status": true,
            # "order_items": "проба",
            # "result_orders_price": 111.0,
            # "delivery_address": "Болото Шрека 23",
            # "contact_telephone": "+797877788823",
            # "user": 1

        result_object = OrderSerializer(order_object[0]).data

        # {'id': 2, 'datetime': '2022-06-23T14:33:59.135991Z', 'pay_status': False, 'execution_status': True,
        # 'order_items': 'товары для Шрека', 'result_orders_price': 111.0, 'need_milling': True,
        # 'shipping': False, 'shipping_address': 'Болото Шрека 23', 'contact_telephone': '+797877788823',
        # 'user': 1}

        return Response(result_object, status.HTTP_200_OK)


# 7
class RemoveOrder(APIView):
    """Представление для удаления заказа из БД. Передай /?id заказа"""

    def get(self, request, format=None):
        order_id = request.query_params.get('id')
        if order_id:
            Order.objects.get(id=order_id).delete()
            return Response(status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)


# 8
class ClearBasket(APIView):
    """Представление для очистки корзины. Необходим параметр запроса /?user_tlg_id=..."""

    def get(self, request, format=None):
        # получение параметров запроса
        user_tlg_id = request.query_params.get('user_tlg_id')

        try:
            if user_tlg_id:
                user = BotUsers.objects.get(user_tlg_id=user_tlg_id)
                # берём записи из корзины пользователя для последующего удаления и "возврата остатков на склад"
                basket_object = OrderBasket.objects.filter(user=user).select_related('items_id')
            else:
                # берём все записи из модели корзины для последующего удаления и "возврата остатков на склад"
                basket_object = OrderBasket.objects.all().select_related('items_id')
            for i_object in basket_object:
                pk = i_object.items_id.pk
                i_item = Items.objects.get(pk=pk)
                i_item.number_of_items += i_object.items_number_in_basket
                i_item.save()
                i_object.delete()
            answer_status = status.HTTP_200_OK
            result_object = {'basket_is_cleaned': 'корзина очищена'}

        except Exception:
            answer_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            result_object = {'some_exception': 'операция не выполнена из-за ошибки'}

        return Response(result_object, answer_status)


# 9
class ItemsDetailView(APIView):
    """Представление для получения детальной информации о товаре"""

    def get(self, request, format=None):
        item_id = request.query_params.get('item_id')
        if item_id:
            item_object = Items.objects.get(pk=item_id)
            result_object = ItemsSerializer(item_object, many=False).data
        else:
            item_objects = Items.objects.all()
            result_object = ItemsSerializer(item_objects, many=True).data
        return Response(result_object, status.HTTP_200_OK)


# 10
class OrderArchiveView(APIView):
    """Представление для работы с моделью архива заказов."""

    def post(self, request, format=None):
        serializer = OrderArchiveSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.data.get('order_id_before_receiving')
            user = BotUsers.objects.get(id=serializer.data.get('user'))
            OrderArchive.objects.create(
                order_id_before_receiving=order_id,
                user=user,
                pay_status=serializer.data.get('pay_status'),
                execution_status=serializer.data.get('execution_status'),
                order_items=serializer.data.get('order_items'),
                result_orders_price=serializer.data.get('result_orders_price'),
                delivery_address=serializer.data.get('delivery_address'),
                contact_telephone=serializer.data.get('contact_telephone'),
                sizes_for_clothes=serializer.data.get('sizes_for_clothes')
            )
            Order.objects.get(pk=order_id).delete()
            return Response(status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)


# 11
class UserView(APIView):
    """Добавление нового пользователя в БД"""

    def get(self, request, format=None):
        user_id = request.query_params.get('user_id')
        user_object = BotUsers.objects.get(id=user_id)
        result_object = BotUsersSerializer(user_object, many=False).data
        return Response(result_object, status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = BotUsersSerializer(data=request.data)
        if serializer.is_valid():
            user_tlg_id = serializer.data.get('user_tlg_id')
            user_object = BotUsers.objects.update_or_create(
                user_tlg_id=user_tlg_id,
                defaults={
                    'user_tlg_id': user_tlg_id,
                    'user_tlg_name': serializer.data.get('user_tlg_name'),
                    'user_name': serializer.data.get('user_name'),
                })
            user_object[0].orders_numb += 1
            result_object = BotUsersSerializer(user_object[0]).data
            return Response(result_object, status.HTTP_200_OK)
        else:
            Response(status.HTTP_400_BAD_REQUEST)
