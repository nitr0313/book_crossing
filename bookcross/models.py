import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

# Create your models here.
User = get_user_model()


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

    def __str__(self):
        return f'{self.id} {self.author} {self.title}'

    class Meta:
        ordering = ('author', 'title')
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Книги'

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    @property
    def get_full_path(self):
        pth = self.place.title
        tmp = self.place
        while tmp.parent_place is not None:
            tmp = tmp.parent_place
            pth = ' > '.join([tmp.title, pth])
        return pth

    def save(self, *args, **kwargs):
        if self.loaner is not None and self.status != 'o' and self.status != 'r':
            self.status = 'r'
            self.reserved_time = datetime.datetime.utcnow()
        super().save(*args, **kwargs)


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
    pass


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
        return self.get_full_path

    @property
    def get_full_path(self):
        pth = self.title
        tmp = self
        while tmp.parent_place is not None:
            tmp = tmp.parent_place
            pth = ' > '.join([tmp.title, pth])
        return pth

    class Meta:
        # ordering = ('title')
        verbose_name = 'Место (шкаф, полка, и тд)'
        verbose_name_plural = 'Места хранения книг'
