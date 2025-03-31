from django.contrib.auth.views import LogoutView
from django.urls import path

from users import views
from users.views import RegisterUser

app_name = 'users'
urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
]
