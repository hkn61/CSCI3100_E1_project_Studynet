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
from user_profile.models import Image
# Create your views here.

USER_AUTH_DB = MONGO_CLIENT['csci3100']['user_auth']
FRIEND_DB = MONGO_CLIENT['chat']['friend']

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        email_ver = request.POST["email_ver"]

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists.")
            return render(request, "auth/signup.html")
        if User.objects.filter(email=email):
            messages.error(request, "Email already exists.")
            return render(request, "auth/signup.html")
        if pass1 != pass2:
            messages.error(request, "Passwords are not the same.")
            return render(request, "auth/signup.html")

        real_auth_token = USER_AUTH_DB.find({"username":username})[0]["token"]
        if email_ver != real_auth_token:
            messages.error(request, "Invalid confirmation code")
            return render(request, "auth/signup.html")

        newUser = User.objects.create_user(username=username, email=email, password=pass1)
        newUser.first_name = fname
        newUser.last_name = lname

        messages.success(request, "Your account has been successfully created.")
        newUser.save()

        FRIEND_DB.insert({"user_name": username, "friend_list": [], "group_list":[], "profile":"/static/profile/default.png"})

        # user = UserModel()
        # user.username = username
        # user.email = email
        # #user.image = 'static/default.png'
        # user.save()

        return index(request)
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
            return redirect("../task/tasklist")
        else:
            messages.error(request, "You have not sign up yet")
            return render(request, "auth/signup.html")
    return render(request, "auth/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("../")

def index(request):
    if request.user.is_authenticated:
        user = request.user
        messages.success(request, f"Hello {user}, You have been successfully signed in.")
    return render(request,"auth/index.html")

def send_email(request):
    username = request.POST["name"]
    email = request.POST["email"]
    # Email
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    subject = "Welcome to StudyNet"
    message = f"Welcome to StudyNet, {username}. Your email verification code is {ran}."
    from_email = settings.EMAIL_HOST_USER
    to_list = [email]

    if USER_AUTH_DB.find({"username":username}).count() != 0:
        USER_AUTH_DB.delete_many({"username":username})


    USER_AUTH_DB.insert_one({"username": username, "token": ran, })
    send_mail(subject, message, from_email, to_list, fail_silently=True)
    return HttpResponse()




