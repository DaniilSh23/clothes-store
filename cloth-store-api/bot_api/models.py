from django.db import models


class BotUsers(models.Model):
    """Пользователи бота"""

    user_tlg_id = models.CharField(verbose_name='ID телеграма пользователя', max_length=50, db_index=True)
    user_tlg_name = models.CharField(verbose_name='Никнейм в телеграме', max_length=100, blank=True, null=True)
    user_name = models.CharField(verbose_name='Имя клиента', max_length=100, blank=True, null=True)
    orders_numb = models.IntegerField(verbose_name='Количество заказов', default=0, blank=True)

    class Meta:
        ordering = ['id']
        db_table = 'Пользователи'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.user_tlg_id)


class Categories(models.Model):
    """Модель для категорий товаров"""

    category_name = models.CharField(max_length=50, verbose_name='Название категории товаров')

    class Meta:
        ordering = ['id']
        db_table = 'Категории товаров'
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.category_name


class Items(models.Model):
    """Модель для товаров"""

    items_name = models.CharField(max_length=50, verbose_name='Название товара')
    description = models.TextField(max_length=4000, verbose_name='Описание товара')
    price = models.FloatField(max_length=10, verbose_name='Цена товара')
    number_of_items = models.IntegerField(verbose_name='Количество товара в наличии')
    items_category = models.ForeignKey(to=Categories, on_delete=models.CASCADE, verbose_name='Категория товаров')
    clothes_size = models.CharField(max_length=20, verbose_name='Доступные размеры', blank=True, null=True)
    image_for_items_id = models.TextField(
        max_length=5000,
        verbose_name='ID картинки для товара(скопировать из бота через пробел)',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['items_name']
        db_table = 'Товары'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.items_name


class OrderBasket(models.Model):
    """Модель для корзины заказа"""

    items_id = models.ForeignKey(to=Items, on_delete=models.CASCADE, verbose_name='ID товара')
    items_number_in_basket = models.IntegerField(verbose_name='Количество данного товара в корзине', default=1)
    user = models.ForeignKey(to=BotUsers, verbose_name='Пользователь', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']
        db_table = 'Товары в корзине'
        verbose_name = 'Товары в корзине'
        verbose_name_plural = 'Товары в корзине'


class Order(models.Model):
    """Модель для заказа"""

    user = models.ForeignKey(to=BotUsers, verbose_name='Пользователь', on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время заказа')
    pay_status = models.BooleanField(default=False, verbose_name='Статус оплаты', db_index=True, blank=True, null=True)
    execution_status = models.BooleanField(default=False, verbose_name='Статус выполнения заказа',
                                           db_index=True, blank=True, null=True)
    order_items = models.TextField(max_length=10000, verbose_name='Товары из заказа', blank=True, null=True)
    result_orders_price = models.FloatField(verbose_name='Итоговая цена заказа', blank=True, default=0)
    delivery_address = models.CharField(verbose_name='Адрес доставки', max_length=500, blank=True, null=True)
    contact_telephone = models.CharField(verbose_name='Контактный телефон', max_length=30, blank=True, null=True)
    sizes_for_clothes = models.CharField(verbose_name='Размеры одежды', max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-datetime']
        db_table = 'Заказы'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.order_items


class OrderArchive(models.Model):
    """Модель для архива заказов, которые были: оплачены --> получены --> выполнены."""

    order_id_before_receiving = models.IntegerField(verbose_name='ID заказа перед получением клиентом')
    user = models.ForeignKey(to=BotUsers, verbose_name='Пользователь', on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время заказа')
    pay_status = models.BooleanField(default=False, verbose_name='Статус оплаты', db_index=True, null=True, blank=True)
    execution_status = models.BooleanField(default=False, verbose_name='Статус выполнения заказа', db_index=True,
                                           null=True, blank=True)
    order_items = models.TextField(max_length=4000, verbose_name='Товары из заказа')
    result_orders_price = models.FloatField(verbose_name='Итоговая цена заказа')
    delivery_address = models.CharField(verbose_name='Адрес доставки', max_length=500, blank=True, null=True)
    contact_telephone = models.CharField(verbose_name='Контактный телефон', max_length=20)
    sizes_for_clothes = models.CharField(verbose_name='Размеры одежды', max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-datetime']
        db_table = 'Архив заказов'
        verbose_name = 'Архив заказа'
        verbose_name_plural = 'Архив заказов'
