from django.shortcuts import render
from django.views.generic import View
from rest_framework.viewsets import ModelViewSet

from bookcross.models import BookInstance


# Create your views here.
from bookcross.serializers import BookInstanceSerializer


def book_detail(request):
    return render(request, 'bookcross/book_detail.html', context={})


class BookInstanceListView(View):
    model = BookInstance
    template = 'bookcross/list_book.html'

    def get(self, request):
        books = None
        if request.user.is_authenticated:
            if request.user.is_active:
                books = BookInstance.objects.filter(status__exact='a')  # Статус available доступна
        con = dict(
            books=books,
            active_page='list_book',
        )

        return render(request, self.template, context=con)


def book_instance_view(request):
    return render(request, 'bookcross/main_app.html')


class BookInstanceView(ModelViewSet):
    queryset = BookInstance.objects.filter(status__exact='a')
    serializer_class = BookInstanceSerializer
