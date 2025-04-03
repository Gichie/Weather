from django.urls import path

from weather.views import IndexView, LocationSearchView

app_name = 'weather'

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('search/', LocationSearchView.as_view(), name='search')
]
