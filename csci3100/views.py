from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import logout
# Create your views here.

def home(request):
    return render(request,"homepage.html")

def signout(request):
    logout(request)
    return render(request, "homepage.html")
