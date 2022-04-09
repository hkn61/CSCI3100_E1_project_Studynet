from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from csci3100 import settings
import random
import string
from csci3100.settings import MONGO_CLIENT
from .models import UserModel
# Create your views here.

def profile(request):
    username = request.session.get('username') or ''
    image = UserModel.objects.filter(username=username)
    return render(request, "user/profile.html", {
        "profile": image,
    })


def updatephoto(request):
    user = UserModel()
    if request.method == "POST":
        username = request.POST.get("username")
    # change profile photo if uploaded
        if len(request.FILES) != 0:
            image = request.FILES.get('image')
            user.objects.filter(username = username).update(image=image)
    
    return render(request, 'user/profile.html', {
        'user': user
    })


def changepwd(request):
    if request.method == "POST":
        username = request.POST["username"]
        pass0 = request.POST["pass0"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        # change password
        if User.objects.filter(username=username):
            user_auth = authenticate(username=username, password=pass0)
            if user_auth is not None:
                if pass1 == pass0:
                    messages.error(request, "Please enter a different password from the old one.")
                    return redirect("profile")
                else:
                    if pass1 == pass2:
                        User.objects.update_or_create(username=username, defaults={'password': pass1})
                    else:
                        messages.error(request, "New passwords are not the same.")
                        return redirect("profile")
            else:
                messages.error(request, "Incorrect old username / password.")
                return redirect("profile")
        else:
            messages.error(request, "Invalid username.")
            return redirect("profile")
    
    return render(request, "user/changepwd.html")