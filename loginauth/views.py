from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from csci3100 import settings
import random
import string
# Create your views here.


def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists.")
            return redirect("signup")
        if User.objects.filter(email=email):
            messages.error(request, "Email already exists.")
            return redirect("signup")

        newUser = User.objects.create_user(username=username, email=email, password=pass1)
        newUser.first_name = fname
        newUser.last_name = lname

        newUser.save()
        messages.success(request, "Your account has been successfully created.")

        # Email
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        subject = "Welcome to StudyNet"
        message = "Hello" + username + "!\n" + "Welcome to StudyNet."
        from_email = settings.EMAIL_HOST_USER
        to_list = [newUser.email]
        send_mail(subject, message, from_email,to_list, fail_silently=True)

        return redirect('signin')

    return render(request, "auth/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["pass1"]

        user_auth = authenticate(username=username, password=password)
        if user_auth is not None:
            login(request, user_auth)
            fname = user_auth.first_name
            messages.success(request, "You have been successfully signed in.")
            return render(request, "auth/index.html", {"fname": fname})
        else:
            messages.error(request, "You have not sign up yet")
            return redirect("signin")
    return render(request, "auth/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("../")

def index(request):
    return render(request,"auth/index.html")


