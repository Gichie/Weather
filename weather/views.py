from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View

from weather import services
from weather.dtos import LocationDTO
from weather.exceptions import WeatherServiceError
from weather.forms import SearchLocationForm


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'weather/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchLocationForm(self.request.GET or None)
        context['search_form'] = search_form
        return context


class LocationSearchView(LoginRequiredMixin, View):
    template_name = 'weather/search.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context: dict[str, Any] = {
            'locations_dto': [],
            'error_message': None,
            'query': '',
            'search_form': SearchLocationForm(self.request.GET or None)
        }

        query = request.GET.get('location', '').strip()
        context['query'] = query

        if query:
            try:
                locations_dto: list[LocationDTO] = services.WeatherAPI.find_locations(query)

                if not locations_dto:
                    context['error_message'] = f'Локации с названием {query} не найднены'
                else:
                    context['locations_dto'] = locations_dto

            except WeatherServiceError as e:
                context['error_message'] = f'Ошибка сервиса при поиске локация: {e}'
                # todo logger
                print(f'Ошибка в LocationSearchView: {e}')

        return render(request, self.template_name, context)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
