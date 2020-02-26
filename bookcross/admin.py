from django.contrib import admin
from django.contrib.admin.decorators import register

from bookcross.models import *

# Register your models here.


admin.site.register(Genre)
admin.site.register(CrossHistory)


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    fields = ['owner', 'title', 'isbn', 'genre', 'status']


@register(Place)
class PlaceAdmin(admin.ModelAdmin):
    # fields = ['author', 'title']
    list_display = ['title', 'get_full_path', 'end']
    list_filter = ['end', 'owner']
    list_editable = ['end']


@register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # fields = ['last_name', 'first_name', 'date_of_birth', 'date_of_death']
    list_display = ['last_name', 'first_name', 'date_of_birth', 'date_of_death']
    inlines = [BooksInstanceInline]


@register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    # fields = ['author', 'title']
    list_display = ['author', 'title', 'status', 'isbn', 'place']
    list_filter = ['owner', 'loaner', 'author', 'status']
    filter_horizontal = ['genre']
