from django.shortcuts import render
from csci3100.settings import MONGO_CLIENT

USER_AUTH_DB = MONGO_CLIENT['csci3100']['task_list']
# Create your views here.
def gettasklist(request):
    if request.user.is_authenticated:
        username = request.user
    return render(request, "task/task.html")


def report(request):
    if request.user.is_authenticated:
        username = request.user
