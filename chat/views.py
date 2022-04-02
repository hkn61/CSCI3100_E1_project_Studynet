from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from asgiref.sync import async_to_sync
from csci3100.settings import MONGO_CLIENT
# Create your views here.
from django.shortcuts import render

def group(request):
    return render(request, 'chat/group.html', {})



def groupadd(request):
    return render(request, 'chat/groupadd.html', {})


def groupchat(request, room_name):
    print('inside room view ======>', room_name)
    username = request.session.get('username') or ''
    if not username:
        return HttpResponseRedirect('homepage/login/')
    filters = {'chat_room': room_name, 'deleted': {'$ne': True}}
    sort_fields = [('timestamp', -1)]
    previous_messages = []
    for chat in MONGO_CLIENT['chat_message']['account_1'].find(filters).sort(sort_fields).limit(20):
        chat['_id'] = str(chat['_id'])
        chat['timestamp'] = chat['timestamp']
        chat['message'] = chat['message']['text']
        previous_messages.append(chat)
    previous_messages = sorted(previous_messages, key=lambda s: s['timestamp'])
    print('previous_messages =======>', previous_messages)
    return render(request, 'chat/groupchat.html', {
        'room_name': room_name,
        'prev_messages': previous_messages,
        'current_user': request.session['username']
    })



def grouplist(request):
    return render(request, 'chat/grouplist.html', {})