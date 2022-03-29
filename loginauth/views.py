from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
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



        return redirect('signin')

    return render(request, "auth/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["pass1"]

        user_auth = authenticate(username=username,password=password)
        if  user_auth is not None:
            login(request, user_auth)
            fname = user_auth.first_name
            messages.success(request, "You have been successfully signed in.")
            return render(request, "auth/index.html", {"fname": fname})
        else:
            messages.error(request, "You have not sign up yet")
            return redirect("../")
    return render(request, "auth/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return render(request, "home.html")
