from django.shortcuts import render, redirect
from csci3100.settings import MONGO_CLIENT
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import json
USER_TASK_DB = MONGO_CLIENT['csci3100']['task_list']
FRIEND_DB = MONGO_CLIENT['chat']['friend']
# Create your views here.

# Render main task page.
def tasklist(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        # messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    return render(request, "task/task.html")

# Get tasklist of user.
def gettasklist(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    user_task_list = USER_TASK_DB.find({"username":str(username)})
    # if user_task_list.count() == 0:
    #     USER_TASK_DB.insert_one({"username": str(username),"tasklist":{},"deletedtask":{}})
    #     return HttpResponse()
    # else:
    existing = user_task_list[0]["tasklist"]
    unfinished_task = {}
    for key, value in existing.items():
        if value["isfinished"] == 0 and value["isworking"] == 0 :
            unfinished_task[key] = value
    return JsonResponse(unfinished_task)

# Add a task.
def inserttask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"]
    user_task_list = USER_TASK_DB.find({"username":str(username)})
    # print(user_task_list[0])
    # if user_task_list.count() == 0:
    #     USER_TASK_DB.insert_one({"username":username,"tasklist":{taskname:{"isworking":0,"isfinished":0,"timespent":0,"FinishedTimestamp":0,}}, "deletedtask":{}})
    # else:
    existing = user_task_list[0]
    existing["tasklist"][taskname] = {"isworking":0,"isfinished":0,"timespent":0,"FinishedTimestamp":0,}
    USER_TASK_DB.update_one({"username":str(username)},{"$set":{"tasklist":existing["tasklist"]}})
    return HttpResponse()

# Delete a task.
def deletetask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"][:-1]
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    existing["deletedtask"][taskname] = {"isworking":0,"isfinished":0,"timespent":0,"FinishedTimestamp":0,}
    del existing["tasklist"][taskname]
    USER_TASK_DB.update_one({"username": str(username)}, {"$set": {"tasklist": existing["tasklist"],"deletedtask": existing["deletedtask"]}})
    return HttpResponse()

# Change working status of a task.
def changedoingstatus(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"][:-1]
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    finished_status = existing["tasklist"][taskname]["isworking"]
    existing["tasklist"][taskname]["isworking"] = 1 - int(finished_status)
    USER_TASK_DB.update_one({"username": str(username)}, {"$set": {"tasklist": existing["tasklist"]}})
    return HttpResponse()

# Render finished task page.
def showfinishedtask(request):
    return render(request, "task/finishedtask.html")

# Get all finished task of user.
def getfinishedtask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    user_task_list = USER_TASK_DB.find({"username":str(username)})
    # if user_task_list.count() == 0:
    #     USER_TASK_DB.insert_one({"username": str(username),"tasklist":{},"deletedtask":{}})
    #     return HttpResponse()
    # else:
    existing = user_task_list[0]["tasklist"]
    finished_task = {}
    for key, value in existing.items():
        if value["isfinished"] == 1:
            finished_task[key] = value
    return JsonResponse(finished_task)

# Restore finished task to task list.
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

# Render Deleted task page.
def showdeletedtask(request):
    return render(request, "task/deletedtask.html")

def getdeletedtask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    user_task_list = USER_TASK_DB.find({"username":str(username)})
    # if user_task_list.count() == 0:
    #     USER_TASK_DB.insert_one({"username": str(username),"tasklist":{},"deletedtask":{}})
    #     return HttpResponse()
    # else:
    return JsonResponse(user_task_list[0]["deletedtask"])

# Restore deleted task to task list.
def restoredeletetask(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"][:-7]
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    existing["tasklist"][taskname] = {"isworking":0,"isfinished":0,"timespent":0,"FinishedTimestamp":0,}
    del existing["deletedtask"][taskname]
    USER_TASK_DB.update_one({"username": str(username)},
                            {"$set": {"tasklist": existing["tasklist"], "deletedtask": existing["deletedtask"]}})
    return HttpResponse()

# Render timer page.
def timer(request):
    return render(request, "task/timer.html")

# Get working task list.
def getdoinglist(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    user_task_list = USER_TASK_DB.find({"username":str(username)})
    # if user_task_list.count() == 0:
    #     USER_TASK_DB.insert_one({"username": str(username),"tasklist":{},"deletedtask":{}})
    #     return HttpResponse()
    # else:
    existing = user_task_list[0]["tasklist"]
    unfinished_task = {}
    for key, value in existing.items():
        if value["isfinished"] == 0 and value["isworking"] == 1 :
            unfinished_task[key] = value
    return JsonResponse(unfinished_task)

# Change finished status of a task.
def changefinishedstatus(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    taskname = request.POST["taskname"].split()[0]
    tmstp = request.POST["tmstp"]
    datelist = tmstp.split(",")[0].split("/")
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    finished_status = existing["tasklist"][taskname]["isfinished"]
    existing["tasklist"][taskname]["isfinished"] = 1- int(finished_status)
    existing["tasklist"][taskname]["FinishedTimestamp"] = datelist
    USER_TASK_DB.update_one({"username": str(username)},{"$set": {"tasklist": existing["tasklist"]}})
    return HttpResponse()

# Add timespent to working tasks.
def addtimespent(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    tasknames = request.POST.get("tasknames").split(",")
    timespent = request.POST.get("time")
    user_task_list = USER_TASK_DB.find({"username": str(username)})
    existing = user_task_list[0]
    # print(timespent)
    for task in tasknames:
        task = task[:-1]
        existing_time = existing["tasklist"][task]["timespent"]
        existing["tasklist"][task]["timespent"] = existing_time + int(timespent)
    USER_TASK_DB.update_one({"username": str(username)}, {"$set": {"tasklist": existing["tasklist"]}})
    return HttpResponse()

# Render report page.
def report(request):
    return render(request, "task/report.html")

# Get report data.
def get_report_data(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    selected_user = request.POST.get("user")

    date_str = request.POST.get("date")
    date_info = date_str.split("-")
    finished_and_matched = []
    if selected_user == "Me":
        user_task_list = USER_TASK_DB.find({"username": str(username)})
        existing = user_task_list[0]
        for task,task_info in existing["tasklist"].items():
            if task_info["FinishedTimestamp"] == 0 or task_info["isfinished"] == 0:continue
            elif int(task_info["FinishedTimestamp"][0]) == int(date_info[1]) and int(task_info["FinishedTimestamp"][1]) == int(date_info[2]) and int(task_info["FinishedTimestamp"][2]) == int(date_info[0]):
                finished_and_matched.append({"taskname":task,"timespent":task_info["timespent"]})
            else:continue
    else:
        username = selected_user
        user_task_list = USER_TASK_DB.find({"username": str(username)})
        existing = user_task_list[0]
        if existing["privacy"] == 0:
            messages.error(request,"The privacy setting of your friend is false")
            print("Error")
            return JsonResponse(-1,safe=False)
        else:

            for task,task_info in existing["tasklist"].items():
                if task_info["FinishedTimestamp"] == 0 or task_info["isfinished"] == 0:continue
                elif int(task_info["FinishedTimestamp"][0]) == int(date_info[1]) and int(task_info["FinishedTimestamp"][1]) == int(date_info[2]) and int(task_info["FinishedTimestamp"][2]) == int(date_info[0]):
                    finished_and_matched.append({"taskname":task,"timespent":task_info["timespent"]})
                else:continue

    return JsonResponse(finished_and_matched,safe=False)

# Get user friend list.
def get_friend_list(request):
    if request.user.is_authenticated:
        username = request.user
    else:
        messages.error(request, "Sign in Error")
        return redirect("../auth/signin")
    user_friend_list = FRIEND_DB.find({"user_name": str(username)})
    friend_list = user_friend_list[0]["friend_list"]
    return JsonResponse(friend_list,safe=False)