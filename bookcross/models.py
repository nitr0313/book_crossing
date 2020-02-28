import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

# Create your models here.
User = get_user_model()

MAX_RESERVED_TIME = datetime.timedelta(hours=24)


class BookInstance(models.Model):
    """
    Модель описывыет конкретный экземпляр книги
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Уникальный ID экземпляра книги")
    title = models.CharField(max_length=200, verbose_name='Название книги')
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, verbose_name='Автор', null=True)
    summary = models.TextField(max_length=1000, verbose_name='Описание', help_text="Короткое описание книги")
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13-ти значный номер базы книг ISBN'
                                      '<a href="https://www.isbn-international.org/content/what-isbn">'
                                      'ISBN number</a>', null=True, blank=True)
    genre = models.ManyToManyField('Genre', verbose_name='Жанр', help_text="Выберите жанры этой книги")
    due_back = models.DateField(null=True, blank=True, verbose_name='В аренде с',
                                help_text="Книга отдана на чтение с этой даты")
    reserved_time = models.DateTimeField(verbose_name='Время резервирования', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец', help_text='Владелец книги',
                              related_name='owner_books')
    loaner = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Заемщик', null=True, blank=True,
                               help_text='Заемщик книги', related_name='loaner_books')
    place = models.ForeignKey('Place', verbose_name='Место хранения', on_delete=models.SET_NULL, null=True, blank=True)
    cover = models.ImageField(verbose_name='Обложка', upload_to="books/%Y/%m/%d", blank=True)

    LOAN_STATUS = (
        ('r', 'Зарезервирована'),
        ('m', 'В ремонте'),
        ('a', 'Доступна'),
        ('x', 'Изьята из обращения'),
        ('o', 'В аренде'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True,
                              verbose_name='Доступность книги', default='a',
                              help_text='Доступность книги')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_status = self.status

    def __str__(self):
        return f'{self.id} {self.author} {self.title}'

    def get_cover_url(self):
        if self.cover and hasattr(self.cover, 'url'):
            return self.cover.url
        return 'media/users/no_image.png'

    class Meta:
        ordering = ('author', 'title')
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Книги'

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def get_time_reserved(self):
        if self.status == 'r' and self.reserved_time:
            dt_now = datetime.datetime.now().replace(tzinfo=None)
            dt_res = self.reserved_time.replace(tzinfo=None)
            # print(f'Сейчас {dt_now},  зарезервирована в {dt_res}')
            if dt_now - dt_res > MAX_RESERVED_TIME:
                return 'Резерв просрочен, продлить или сделать сделать доступной'
            else:
                return MAX_RESERVED_TIME - (dt_now - dt_res)
        return 'Книга не зарезервирована'

    get_time_reserved.short_description = 'Время до конца резерва'

    @property
    def get_full_path(self):
        pth = self.place.title
        tmp = self.place
        while tmp.parent_place is not None:
            tmp = tmp.parent_place
            pth = ' > '.join([tmp.title, pth])
        return pth

    def get_rating(self):
        rates = BookRating.objects.filter(book=self)
        if not len(rates):
            return 0
        # print(rates)
        return sum([int(r.rating) for r in rates]) / len(rates)

    def favorite_count(self):
        return Favorite.objects.all().count()

    def save(self, *args, **kwargs):
        # print(self.status)
        if self.status != self.old_status:
            lstat = dict(self.LOAN_STATUS)
            ch = CrossHistory()
            ch.book = self
            ch.loaner = self.loaner
            ch.comment = f'Статус книги изменен c {lstat[self.old_status]} на {lstat[self.status]}'
            ch.save()

            if self.status == 'o':
                self.reserved_time = None
            elif self.status == 'r':
                self.reserved_time = datetime.datetime.now().replace(tzinfo=None)

        # if self.loaner is not None and self.status != 'o' and self.status != 'r':
        #     self.status = 'r'
        #     if self.reserved_time is None:
        #         print('Произошла смена времени резервирования')

        return super().save(*args, **kwargs)


class BookRating(models.Model):
    """
    Отценки поставленные пользотвалем книге
    """
    book = models.ForeignKey('BookInstance', on_delete=models.CASCADE, related_name='book_rating')
    RATING = (
        ('5', 5),
        ('4', 4),
        ('3', 3),
        ('2', 2),
        ('1', 1),
    )
    rating = models.CharField(max_length=1, choices=RATING, verbose_name="Мнение пользователя о книге", default='5')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.book} {self.rating} {self.user}'

    class Meta:
        verbose_name_plural = 'Отценки пользователей'
        verbose_name = 'Отценка пользователя'
        ordering = ('book', 'rating')
        unique_together = ('book', 'user')


class Favorite(models.Model):
    book = models.ForeignKey('BookInstance', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Пользователь {self.user} добавил в избранное книгу {self.book}'

    class Meta:
        verbose_name = 'Унига помещенная в избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('book', 'create_date')


class Author(models.Model):
    """
    Модель описывает автора книг
    """
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    date_of_birth = models.DateField('Дата рождения', null=True, blank=True)
    date_of_death = models.DateField('Умер', null=True, blank=True)

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

    # def get_absolute_url(self):
    #     return reverse('author-detail', args=[str(self.id)])
    class Meta:
        verbose_name_plural = 'Авторы'
        verbose_name = 'Автор'


class Genre(models.Model):
    """
    Модель описывающая жанры книг (Фантастика, Детектив и тд)
    """
    name = models.CharField(max_length=200, help_text='Все возможные жанры книг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class CrossHistory(models.Model):
    book = models.ForeignKey('BookInstance', on_delete=models.CASCADE, default=None, null=True, verbose_name='Книга')
    create_date = models.DateField(auto_now_add=True, verbose_name='Дата создания', null=True)
    loaner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Заемщик')
    comment = models.CharField(max_length=100, verbose_name='Описание', blank=True, null=True)

    def __str__(self):
        return f'{self.book}'

    class Meta:
        ordering = ('book', 'create_date')
        verbose_name_plural = 'Истории перемещения книг'
        verbose_name = 'Перемещение книги'


class Place(models.Model):
    """
    Место хранения книги
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_places')
    title = models.CharField(max_length=100, help_text='Место хранения книги шкаф, полка, стол, 3я справа')
    parent_place = models.ForeignKey('Place', verbose_name='Находится в...', on_delete=models.CASCADE, null=True,
                                     blank=True,
                                     related_name="inside_places")
    end = models.BooleanField(verbose_name="Конечное место", default=False, help_text="Конечное место где стоят книги?")

    def __str__(self):
        return self.get_full_path()

    def get_full_path(self):
        pth = self.title
        tmp = self
        while tmp.parent_place is not None:
            tmp = tmp.parent_place
            pth = ' > '.join([tmp.title, pth])
        return pth

    get_full_path.short_description = 'Находится в...'

    class Meta:
        # ordering = ('title')
        verbose_name = 'Место (шкаф, полка, и тд)'
        verbose_name_plural = 'Места хранения книг'
