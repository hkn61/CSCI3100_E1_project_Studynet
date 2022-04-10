from os import times
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from asgiref.sync import async_to_sync
#from importlib_metadata import re
from csci3100.settings import MONGO_CLIENT
from django.contrib import messages
from bson.objectid import ObjectId
import string
import datetime
# Create your views here.

# test
def save_to_database(db, collection, chat_message):
    print('inside save_to_database====>', db, collection, chat_message)
    r = MONGO_CLIENT[db][collection].insert_one(chat_message)
    return True, r.inserted_id


# update db when create a group
def create_a_group(db, collection, group_info):
    print('inside save_to_ group database====>', db, collection, group_info)
    r = MONGO_CLIENT[db][collection].insert_one()
    return True, r.inserted_id


def create_friend_chat(db, collection, friend_info):
    print('inside save_to_ friend_chat database====>', db, collection, friend_info)
    r = MONGO_CLIENT[db][collection].insert_one()
    return True, r.inserted_id


# update db when add a group
def add_a_group(db, collection, group_name, user_name):
    print('inside add_to_ group database====>', db, collection, group_name, user_name)
    filter = { 'group_name': group_name }
    entry = MONGO_CLIENT[db][collection].find(filter)
    # ??? update member number
    member_num = entry[0]['member_num'] + 1 
    r = MONGO_CLIENT[db][collection].update_one(filter, {'$push': {'member': user_name}, "$set": {'member_num': member_num}}, upsert = True)
    return True, r.inserted_id


def add_a_friend(db, collection, adder, added):
    print('inside add_to_ friend database====>', db, collection, adder, added)
    filter = { 'user_name': adder }
    r = MONGO_CLIENT[db][collection].update_one(filter, {'$push': {'friend_list': added}}, upsert = True)
    filter = { 'user_name': added }
    r = MONGO_CLIENT[db][collection].update_one(filter, {'$push': {'friend_list': adder}}, upsert = True)
    group_name = adder + '&' + added
    group_info = {'group_name': group_name, 'adder': adder, 'added': added}
    status, inserted_id = create_friend_chat('chat', 'friend_chat', group_info)
    return status, inserted_id


def group(request):
    return render(request, 'chat/group.html', {})



def groupadd(request):
    # ??? add a group
    if request.method == "POST":
        group_name = request.POST["groupname"]

        username = ''
        if request.user.is_authenticated:
            username = request.user
            add_a_group('chat', 'group', group_name, username)
        
    return render(request, 'chat/groupadd.html', {})


def groupcreate(request):
    # ??? create a group
    username = ''
    if request.user.is_authenticated:
        username = request.user
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

    return render(request, 'chat/groupcreate.html', {})


def groupsearch(request):
    username = ''
    if request.user.is_authenticated:
        username = request.user
    username = 'Wendy' #test!!!
    group_name = request.POST["groupname"]
    search_by = request.POST.get('search_type')
    res_group_list = []
    #print(search_by)
    addedquery = {'user_name': username}
    user_record = MONGO_CLIENT['chat']['friend'].find(addedquery)

    if search_by == 'public_group': # search by group name, only public result will be returned
        myquery = { "group_name": { "$regex": ".*" + group_name + ".*" } }
        result = MONGO_CLIENT['chat']['group'].find(myquery)
        added_group_list = user_record[0]['group_list']
        # generate (partial) matched result
        for record in result:
            #print(record)
            if not record['private']:
                res_group_list.append(record['group_name'])

    elif search_by == 'private_group': # search by id, matched result will be returned
        if not all(c in string.hexdigits for c in group_name):
            pass
        else:
            myquery = {'_id': ObjectId(group_name)}
            result = MONGO_CLIENT['chat']['group'].find(myquery)
            added_group_list = user_record[0]['group_list']
            for record in result:
                res_group_list.append(record['group_name'])

    else:
        if not all(c in string.hexdigits for c in group_name):
            pass
        else:
            myquery = {'_id': ObjectId(group_name)} # friend id
            result = MONGO_CLIENT['chat']['friend'].find(myquery)
            added_group_list = user_record[0]['friend_list'] # added friend list
            for record in result:
                print(record)
                res_group_list.append(record['user_name']) # matched user
    #print(res_group_list)
    result_group_list = [i for i in res_group_list if i not in added_group_list]

    '''
    ########## test ##########
    timestamp = datetime.datetime.now()
    chat_data = {'group_name': group_name, 'sender': 'hkn', 'time': timestamp, 'message': 'This is the second message.'}
    status, inserted_id = save_to_database('chat', 'chat_message', chat_data)
    print(chat_data)
    if status:
        print('chat saved to db successfully ====>', inserted_id)
    else:
        print('saving to db failed')
    ########## test ##########
    '''

    print(result_group_list)
    return render(request, 'chat/groupadd.html', {
        'res_group_list': result_group_list
        
    })



def groupchat(request, room_name):
    type = room_name[:1]
    room_name = room_name[1:]
    room_name = 'groupthree'
    print(type)
    print('inside room view ======>', room_name)
    group_name = room_name
    username = ''
    if request.user.is_authenticated:
        username = request.user
    username = 'Wendy' #test!!!!!!
    if not username:
        return HttpResponseRedirect('homepage/login/')

    if type == 'g':
        filters = {'group_name': group_name}
        sort_fields = [('time', -1)]
        previous_messages = []
        for chat in MONGO_CLIENT['chat']['chat_message'].find(filters).sort(sort_fields).limit(20):
            print(chat)
            chat['sender'] = str(chat['sender'])
            chat['time'] = chat['time']
            chat['message'] = chat['message']
            previous_messages.append(chat)
        previous_messages = sorted(previous_messages, key=lambda s: s['time'])

    if type == 'f':
        group_name = username + '&' + room_name
        filters = {'group_name': group_name}
        sort_fields = [('time', -1)]
        previous_messages = []
        for chat in MONGO_CLIENT['chat']['chat_message'].find(filters).sort(sort_fields).limit(20):
            print(chat)
            chat['sender'] = str(chat['sender'])
            chat['time'] = chat['time']
            chat['message'] = chat['message']
            previous_messages.append(chat)

        group_name = room_name + '&' + username
        sort_fields = [('time', -1)]
        for chat in MONGO_CLIENT['chat']['chat_message'].find(filters).sort(sort_fields).limit(20):
            print(chat)
            chat['sender'] = str(chat['sender'])
            chat['time'] = chat['time']
            chat['message'] = chat['message']
            previous_messages.append(chat)

        previous_messages = sorted(previous_messages, key=lambda s: s['time'])

    for chat in previous_messages:
        timestamp = chat['time']
        day = timestamp.day
        month = timestamp.month
        year = timestamp.year
        hour = timestamp.hour
        minute = timestamp.minute
        time = str(day) + '/' + str(month) + '/' + str(year) + ' ' + str(hour).zfill(2) + ':' + str(minute).zfill(2)
        chat['time'] = time
        
    print('previous_messages =======>', previous_messages)
    return render(request, 'chat/groupchat.html', {
        'room_name': room_name,
        'prev_messages': previous_messages,
        'current_user': username
    })



def friendadd(request):
    if request.method == "POST":
        friend_name = request.POST["friendname"]
    username = ''
    if request.user.is_authenticated:
        username = request.user
        add_a_friend('chat', 'friend', username, friend_name)
        
    return render(request, 'chat/groupadd.html', {})



def grouplist(request):
    #username = request.session.get('username') or ''
    username = "test"
    filter = {'user_name': username}
    user_record = MONGO_CLIENT['chat']['friend'].find(filter)
    group_list = user_record[0]['group_list']
    friend_list = user_record[0]['friend_list']
    group = []
    for i in range(len(group_list)):
        tmp = MONGO_CLIENT['chat']['group'].find({"group_name": group_list[i]})
        id = tmp[0]['_id']
        dict = {"group_name": group_list[i], "group_id": str(id)}
        group.append(dict)   
    print(group)

    friend = []
    for i in range(len(friend_list)):
        tmp = MONGO_CLIENT['chat']['friend'].find({"user_name": friend_list[i]})
        id = tmp[0]['_id']
        dict = {"friend_name": friend_list[i], "friend_id": str(id)}
        friend.append(dict)
    print(friend)

    return render(request, 'chat/grouplist.html', {
        'group_list': group,
        'friend_list': friend,
        #'current_user': request.session['username']
        'current_user': "test"
    })