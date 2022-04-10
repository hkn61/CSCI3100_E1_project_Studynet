from django.shortcuts import render, redirect
from csci3100.settings import MONGO_CLIENT
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import json
USER_TASK_DB = MONGO_CLIENT['csci3100']['task_list']
# Create your views here.
def tasklist(request):
    return render(request, "task/task.html")

def gettasklist(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    user_task_list = USER_TASK_DB.find({"username":str(username)})
    if user_task_list.count() == 0:
        USER_TASK_DB.insert_one({"username": str(username),"tasklist":{},"deletedtask":{}})
        return HttpResponse()
    else:
        return JsonResponse(user_task_list[0]["tasklist"])
def report(request):
    if request.user.is_authenticated:
        username = request.user


def inserttask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"]
    user_task_list = USER_TASK_DB.find({"username":str(username)})
    # print(user_task_list[0])
    if user_task_list.count() == 0:
        USER_TASK_DB.insert_one({"username":username,"tasklist":{taskname:{"isfinished":0,"timespent":0}}, "deletedtask":{}})
    else:
        existing = user_task_list[0]
        existing["tasklist"][taskname] = {"isfinished":0,"timespent":0}
        USER_TASK_DB.update_one({"username":str(username)},{"$set":{"tasklist":existing["tasklist"]}})
    return HttpResponse()

def deletetask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"][:-1]
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    existing["deletedtask"][taskname] = {"isfinished": 0, "timespent": 0}
    del existing["tasklist"][taskname]
    USER_TASK_DB.update_one({"username": str(username)}, {"$set": {"tasklist": existing["tasklist"],"deletedtask": existing["deletedtask"]}})
    return HttpResponse()
