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
from .models import Image
# Create your views here.

def profile(request):
    username = ''
    if request.user.is_authenticated:
        username = request.user
    username = "1"
    filter = {'user_name': username}
    record = MONGO_CLIENT['chat']['friend'].find_one(filter)
    print(record)
    id = str(record['_id'])
    image = record['profile']

    filter = {'username': username}
    record = MONGO_CLIENT['csci3100']['task_list'].find_one(filter)
    privacy = record['privacy']
    status = "private"
    if privacy == 1:
        status = "public"

    return render(request, "user/profile.html", {
        'username': username,
        'id': id,
        "image": image,
        "status": status
    })


def updatephoto(request):
    username = ''
    if request.user.is_authenticated:
        username = request.user
    if request.method == 'GET':
        return render(request, 'user/profile.html')
    if request.method == "POST":
        username = '1'
    # change profile photo if uploaded
        #if len(request.FILES) != 0:
        image = request.POST.get('image')
        #print(request)
        #user.objects.filter(username = username).update(image=image)
        #images = Image(username=username, image=image)
        #print(images.image)
        #images.save()
        image = '/static/profile/' + image
        print("image chosen:", image)
        filter = {'user_name': username}
        MONGO_CLIENT['chat']['friend'].update_one(filter, {"$set": {'profile': image}}, upsert = True)

        record = MONGO_CLIENT['chat']['friend'].find_one(filter)
        print(record)
        id = str(record['_id'])

        filter = {'username': username}
        record = MONGO_CLIENT['csci3100']['task_list'].find_one(filter)
        privacy = record['privacy']
        status = "private"
        if privacy == 1:
            status = "public"

        return render(request, 'user/profile.html', {
            'username': username,
            'id': id,
            "image": image,
            "status": status
        })


def updateprivacy(request):
    username = ''
    if request.user.is_authenticated:
        username = request.user
    if request.method == "POST":
        username = '1'
        privacy = request.POST.get("privacy")
        filter = {"username": username}
        if privacy == "0":
            MONGO_CLIENT['csci3100']['task_list'].update_one(filter, {"$set": {'privacy': 0}}, upsert = True)
            status = "private"
        else:
            MONGO_CLIENT['csci3100']['task_list'].update_one(filter, {"$set": {'privacy': 1}}, upsert = True)
            status = "public"

        filter = {"user_name": username}
        record = MONGO_CLIENT['chat']['friend'].find_one(filter)
        id = str(record['_id'])
        image = record['profile']

        return render(request, 'user/profile.html', {
            'username': username,
            'id': id,
            "image": image,
            "status": status
        })




def changepwd(request):
    if request.method == "POST":
        username = request.POST["username"]
        pass0 = request.POST["pass0"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        # change password
        user_auth = authenticate(username=username, password=pass0)
        if user_auth is not None:
            if pass1 == pass0:
                messages.error(request, "Please enter a different password from the old one.")
                return redirect("profile")
            else:
                if pass1 == pass2:
                    u = User.objects.get(username=username)
                    u.set_password(pass1)
                    u.save()
                    messages.success(request, "Your password is changed successfully.")
                else:
                    messages.error(request, "New passwords are not the same.")
                    return redirect("profile")
        else:
            messages.error(request, "Incorrect old username / password.")
            return redirect("profile")
        
    
    return render(request, "user/changepwd.html")