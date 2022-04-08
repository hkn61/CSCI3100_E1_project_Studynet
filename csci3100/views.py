from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return render(request,"homepage.html")

def about(request):
    return render(request,"about.html")

def support(request):
    return render(request,"support.html")