from django.shortcuts import render, redirect
from csci3100.settings import MONGO_CLIENT
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import json
USER_TASK_DB = MONGO_CLIENT['csci3100']['task_list']
# Create your views here.
def tasklist(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        # messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
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
        existing = user_task_list[0]["tasklist"]
        unfinished_task = {}
        for key, value in existing.items():
            if value["isfinished"] == 0:
                unfinished_task[key] = value
        return JsonResponse(unfinished_task)

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

def changefinishedstatus(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"].split()[0]
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    finished_status = existing["tasklist"][taskname]["isfinished"]
    existing["tasklist"][taskname]["isfinished"] = 1- int(finished_status)
    USER_TASK_DB.update_one({"username": str(username)},{"$set": {"tasklist": existing["tasklist"]}})
    return HttpResponse()


def showfinishedtask(request):
    return render(request, "task/finishedtask.html")

def getfinishedtask(request):
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
        existing = user_task_list[0]["tasklist"]
        finished_task = {}
        for key, value in existing.items():
            if value["isfinished"] == 1:
                finished_task[key] = value
        return JsonResponse(finished_task)

def restorefinishedtask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"][:-7]
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    finished_status = existing["tasklist"][taskname]["isfinished"]
    existing["tasklist"][taskname]["isfinished"] = 1- int(finished_status)
    USER_TASK_DB.update_one({"username": str(username)},{"$set": {"tasklist": existing["tasklist"]}})
    return HttpResponse()

def showdeletedtask(request):
    return render(request, "task/deletedtask.html")

def getdeletedtask(request):
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
        return JsonResponse(user_task_list[0]["deletedtask"])


def restoredeletetask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"][:-7]
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    existing["tasklist"][taskname] = {"isfinished": 0, "timespent": 0}
    del existing["deletedtask"][taskname]
    USER_TASK_DB.update_one({"username": str(username)},
                            {"$set": {"tasklist": existing["tasklist"], "deletedtask": existing["deletedtask"]}})
    return HttpResponse()
def report(request):
    pass