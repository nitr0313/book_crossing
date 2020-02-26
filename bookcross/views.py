from django.shortcuts import render

# Create your views here.
def book_detail(request):
    return render(request, 'bookcross/book_detail.html', context={})
