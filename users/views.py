from django.http import HttpResponse
from django.shortcuts import render


def login_user(request):
    return render(request, 'users/login.html')


def logout_user(request):
    return HttpResponse('logout')
