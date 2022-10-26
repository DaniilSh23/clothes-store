from rest_framework.pagination import LimitOffsetPagination


class CategoryPagination(LimitOffsetPagination):
    '''
    Переопределенный мной класс пагинации для категорий товаров.
    Категории товаров выводим по 4 на странице, всё остальное,
    где нужна пагинация, по 2 (это указано в глобальных настройках проекта).
    '''
    def paginate_queryset(self, queryset, request, view=None):
        self.limit = 4  # Единственное, что изменил. Категории товаров выводим по 4 на странице
        if self.limit is None:
            return None

        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])
