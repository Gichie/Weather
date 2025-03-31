from django.urls import path

from weather.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='home')
]
