from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from asgiref.sync import async_to_sync
from csci3100.settings import MONGO_CLIENT
from django.contrib import messages
# Create your views here.

# update db when create a group
def create_a_group(db, collection, group_info):
    print('inside save_to_database====>', db, collection, group_info)
    r = MONGO_CLIENT[db][collection].insert_one()
    return True, r.inserted_id


# update db when add a group
def add_a_group(db, collection, group_name, user_name):
    print('inside add_to_database====>', db, collection, group_name, user_name)
    filter = { 'group_name': group_name }
    entry = MONGO_CLIENT[db][collection].find(filter)
    # ??? update member number
    member_num = entry['member_num'] + 1 
    r = MONGO_CLIENT[db][collection].update_one(filter, {'$push': {'member': user_name}, "$set": {'member_num': member_num}}, upsert = True)
    return True, r.inserted_id


def group(request):
    return render(request, 'chat/group.html', {})



def groupadd(request):
    # ??? add a group
    username = request.session.get('username') or ''
    if request.method == "POST":
        group_name = request.POST["groupname"]
    

    return render(request, 'chat/groupadd.html', {})


def groupcreate(request):
    # ??? create a group
    username = request.session.get('username') or ''
    if request.method == "POST":
        group_name = request.POST["groupname"]
        member = [username]
        membernum = 1
        description = request.POST["description"]
        private = request.POST["private"]

        filter = { 'group_name': group_name }
        if MONGO_CLIENT['chat']['group'].find(filter):
            messages.error(request, "Group name already exists.")
            return redirect("groupcreate")

        group_info = {'group_name': group_name, 'member': member, 'member_num': membernum, 'description': description, 'private': private}
        status, inserted_id = create_a_group('chat', 'group', group_info)
        if status:
            print('new group saved to db successfully ====>', inserted_id)
        else:
            print('saving to group db failed')

        user_filter = {'user_name': username}
        # add the new group to the group list of the group creater
        MONGO_CLIENT['chat']['friend'].update_one(user_filter, {'$push': {'group_list': group_name}}) 

    return render(request, 'chat/groupadd.html', {})


def groupsearch(request):
    group_name = request.POST["groupname"]
    myquery = { "group_name": { "$regex": ".*" + group_name + ".*" } }
    result = MONGO_CLIENT['chat']['group'].find(myquery)
    res_group_list = []
    # generate (partial) matched result
    for record in result:
        if not record['private']:
            res_group_list.append(record['group_name'])

    return render(request, 'chat/groupadd.html', {
        'res_group_list': res_group_list
    })


def groupchat(request, room_name):
    print('inside room view ======>', room_name)
    username = request.session.get('username') or ''
    if not username:
        return HttpResponseRedirect('homepage/login/')
    filters = {'chat_room': room_name, 'deleted': {'$ne': True}}
    sort_fields = [('time', -1)]
    previous_messages = []
    for chat in MONGO_CLIENT['chat']['chat_message'].find(filters).sort(sort_fields).limit(20):
        chat['_id'] = str(chat['_id'])
        chat['time'] = chat['time']
        chat['message'] = chat['message']['text']
        previous_messages.append(chat)
    previous_messages = sorted(previous_messages, key=lambda s: s['time'])
    print('previous_messages =======>', previous_messages)
    return render(request, 'chat/groupchat.html', {
        'room_name': room_name,
        'prev_messages': previous_messages,
        'current_user': request.session['username']
    })



def grouplist(request):
    username = request.session.get('username') or ''
    filter = {'user_name': username}
    user_record = MONGO_CLIENT['chat']['friend'].find(filter)
    group_list = user_record['group_list']
    friend_list = user_record['friend_list']

    return render(request, 'chat/grouplist.html', {
        'group_list': group_list,
        'friend_list': friend_list,
        'current_user': request.session['username']
    })