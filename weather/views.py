from decimal import Decimal
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseNotFound, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, ListView

from weather import services
from weather.dtos import LocationDTO
from weather.exceptions import WeatherServiceError
from weather.forms import SearchLocationForm
from weather.models import Location


class IndexView(LoginRequiredMixin, ListView):
    template_name = 'weather/index.html'
    context_object_name = 'locations'

    def get_queryset(self):
        locations = Location.objects.filter(user=self.request.user)
        return locations

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchLocationForm(self.request.GET or None)
        return context


class LocationSearchView(LoginRequiredMixin, View):
    template_name = 'weather/search.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context: dict[str, Any] = {
            'locations_dto': [],
            'error_message': None,
            'search_form': SearchLocationForm()
        }

        query = request.GET.get('location', '').strip()

        if query:
            try:
                locations_dto: list[LocationDTO] = services.WeatherAPI.find_locations(query)
                if not locations_dto:
                    context['error_message'] = f'Локации с названием {query} не найднены'
                else:
                    context['locations_dto'] = locations_dto

            except WeatherServiceError as e:
                context['error_message'] = f'Ошибка сервиса при поиске локаций: {e}'
                # todo logger
                print(f'Ошибка в LocationSearchView: {e}')

        return render(request, self.template_name, context)

    def post(self, request):
        name = request.POST.get('location_name')
        country = request.POST.get('location_country')
        try:
            Location.objects.create(
                name=name,
                country=country,
                user=request.user,
                latitude=Decimal(request.POST.get('location_latitude').replace(',', '.')),
                longitude=Decimal(request.POST.get('location_longitude').replace(',', '.')),
            )
            # todo logger Успешно добавлено
            return redirect('weather:home')
        except (TypeError, ValueError):
            return redirect('weather:search')
        except IntegrityError:
            # todo logger
            messages.error(request, f"Выбранная локация <{name}, {country}> уже добавлена в вашу коллекцию")
            return redirect('weather:home')


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
