from django.http import HttpResponse, HttpResponseNotFound


def index(request):
    return HttpResponse('Страница приложения погода')


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
