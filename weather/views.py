from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.views.generic import TemplateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'weather/index.html'


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
