import logging
from decimal import Decimal
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, ListView

from weather import services
from weather.dtos import LocationDTO
from weather.exceptions import GeocodingApiError
from weather.forms import SearchLocationForm
from weather.models import Location
from weather.services import WeatherAPI

logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, ListView):
    template_name = 'weather/index.html'
    context_object_name = 'locations_weather'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchLocationForm(self.request.GET or None)
        return context

    def get_queryset(self):
        logger.info(f'Получение списка локаций из БД для <{self.request.user}>')
        locations = Location.objects.filter(user=self.request.user)
        locations_weather = []
        logger.info(f'Получение текущей погоды для <{self.request.user}>')
        for location in locations:
            locations_weather.append(
                WeatherAPI.get_weather(location.latitude, location.longitude, location.name))
        return locations_weather

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)

        except GeocodingApiError as e:
            logger.error(f"Geocoding API Error for user {request.user}: {e}", exc_info=True)
            context = {
                'error_title': "Ошибка сервиса геолокации",
                'error_message': f"Произошла ошибка при работе с сервисом геолокации. {e} Попробуйте обновить страницу позже."
            }
            return render(request, 'weather/API_error.html', context, status=503)

    def post(self, request):
        try:
            latitude = Decimal(request.POST.get('latitude').replace(',', '.'))
            longitude = Decimal(request.POST.get('longitude').replace(',', '.'))
            location = Location.objects.get(user=request.user, latitude=latitude, longitude=longitude)
            location.delete()
            logger.info(f'{self.request.user} удалил локацию из сохраненного списка')
            messages.success(request, "Локация удалена.")
        except Location.DoesNotExist:
            logger.warning(f"Локация для удаления для {request.user} не найдена в БД", exc_info=True)
            messages.error(request, 'Локация не найдена')
        except Exception as e:
            logger.error(f"Ошибка при удалении for user {request.user}: {e}", exc_info=True)
            messages.error(request, f"Ошибка при удалении: {str(e)}")

        return redirect('weather:home')


class LocationSearchView(LoginRequiredMixin, View):
    template_name = 'weather/search.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        query = request.GET.get('location', '').strip()
        context: dict[str, Any] = {
            'locations_dto': [],
            'error_message': None,
            'search_form': SearchLocationForm(),
            'query': query,
        }
        if query:
            try:
                locations_dto: list[LocationDTO] = services.WeatherAPI.get_locations(query)
                if not locations_dto:
                    messages.warning(request, f"Локация {query} не найдена")
                else:
                    context['locations_dto'] = locations_dto

            except GeocodingApiError as e:
                context['error_message'] = f'Ошибка сервиса при поиске локаций: {e}'
                # todo logger
                print(f'Ошибка в LocationSearchView: {e}')
                return render(request, 'weather/API_error.html', context, status=503)

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
            return redirect('weather:home')
        except IntegrityError:
            # todo logger
            messages.warning(request, f"Выбранная локация {name}, {country} уже добавлена в вашу коллекцию")
            return redirect('weather:home')


def page_not_found(request, exception):
    return render(request, '404.html', status=404)
