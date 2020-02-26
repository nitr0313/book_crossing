from django.contrib import admin
from django.contrib.admin.decorators import register

from bookcross.forms import BookInstanceForm
from bookcross.models import *

# Register your models here.


admin.site.register(Genre)


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    fields = ['owner', 'title', 'isbn', 'genre', 'status']


@register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_full_path', 'end']
    list_filter = ['end', 'owner']
    list_editable = ['end']


@register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'date_of_birth', 'date_of_death']
    inlines = [BooksInstanceInline]


@register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'status', 'get_time_reserved', 'isbn', 'place']
    list_filter = ['owner', 'loaner', 'author', 'status']
    filter_horizontal = ['genre']
    form = BookInstanceForm


@register(CrossHistory)
class CrossHistoryAdmin(admin.ModelAdmin):
    list_display = ['book', 'comment']
    list_filter = ['book']
