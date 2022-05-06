from os import times
from re import search
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from asgiref.sync import async_to_sync
from numpy import rec
from csci3100.settings import MONGO_CLIENT
from django.contrib import messages
from bson.objectid import ObjectId
import string
import datetime
# Create your views here.

def save_to_database(db, collection, chat_message):
    print('inside save_to_database====>', db, collection, chat_message)
    r = MONGO_CLIENT[db][collection].insert_one(chat_message)
    return True, r.inserted_id


# update db when create a group
def create_a_group(db, collection, group_info):
    print('inside save_to_ group database====>', db, collection, group_info)
    r = MONGO_CLIENT[db][collection].insert_one(group_info)
    return True, r.inserted_id


# update friend_chat db when add a friend
def create_friend_chat(db, collection, friend_info):
    print('inside save_to_ friend_chat database====>', db, collection, friend_info)
    r = MONGO_CLIENT[db][collection].insert_one(friend_info)
    return True, r.inserted_id


# update db when add a group
def add_a_group(db, collection, group_name, user_name):
    print('inside add_to_ group database====>', db, collection, group_name, user_name)
    print(type(group_name))
    filter = { 'group_name': group_name }
    entry = MONGO_CLIENT[db][collection].find_one(filter)
    group_name = str(group_name)
    member_num = entry['memberNum'] + 1 
    if user_name not in entry['member']:
        r = MONGO_CLIENT[db][collection].update_one(filter, {'$push': {'member': user_name}, "$set": {'memberNum': member_num}}, upsert = True)
    else:
        return False
    filter = {'user_name': user_name}
    entry = MONGO_CLIENT[db]['friend'].find(filter)
    if group_name not in entry[0]['group_list']:
        r = MONGO_CLIENT[db]['friend'].update_one(filter, {'$push': {'group_list': group_name}}, upsert = True)
    else:
        return False
    return True


# update friend_chat db when add a friend
def add_a_friend(db, collection, adder, added):
    print('inside add_to_ friend database====>', db, collection, adder, added)
    filter = { 'user_name': adder }
    entry = MONGO_CLIENT[db][collection].find(filter)
    if added not in entry[0]['friend_list']:
        r = MONGO_CLIENT[db][collection].update_one(filter, {'$push': {'friend_list': added}}, upsert = True)
    else:
        return False
    filter = { 'user_name': added }
    entry = MONGO_CLIENT[db][collection].find(filter)
    if adder not in entry[0]['friend_list']:
        r = MONGO_CLIENT[db][collection].update_one(filter, {'$push': {'friend_list': adder}}, upsert = True)
    else:
        return False
    group_name = adder + '&' + added
    group_info = {'group_name': group_name, 'adder': adder, 'added': added}
    status, inserted_id = create_friend_chat('chat', 'friend_chat', group_info)
    return True


def group(request):
    return render(request, 'chat/group.html', {})


'''
If add a group: 
In the friend database, the group list for the current user will be updated. 
In the group database, the group member list and the member number will be updated.

If add a friend:
In the friend database, the friend lists for both the current user and the added friend will be updated. 
In the friend_chat database, a private chat for the two new friends will be created.
'''
def groupadd(request):
    # add a group
    username = ''
    status = True
    indicator = 1
    if request.user.is_authenticated:
        username = request.user
        username = str(username)
    else:
        return redirect("/auth/signin")
    if request.method == "POST":
        group_name = request.POST.get("groupname")
        search_by = request.POST.get("search_by")
        #username = 'Wendy'
        if search_by == 'friend':
            status = add_a_friend('chat', 'friend', username, group_name)
        else:
            status = add_a_group('chat', 'group', group_name, username)
        if not status:
            print(status)
            #messages.error(request, "Request failed when adding {}.".format(group_name))
            #return redirect("groupadd")
    if status:
        indicator = 1
    else:  
        indicator = 0
    return render(request, 'chat/groupadd.html', {
        "indicator": indicator
    })


'''
The function will check whether the group name is the same as an existing one in the 
database. If yes, “group name already exists” message will be shown, and the group will 
not be created. Otherwise, the group will be created and added to the creator’s group list.
'''
def groupcreate(request):
    # create a group
    username = ''
    if request.user.is_authenticated:
        username = request.user
        username = str(username)
    else:
        return redirect("/auth/signin")
    if request.method == "POST":
        group_name = request.POST["groupname"]
        member = [username]
        membernum = 1
        description = request.POST["description"]
        private = request.POST.get("private")

        if private is not None:
            private = 1
        else:
            private = 0

        filter = { 'group_name': group_name }
        if MONGO_CLIENT['chat']['group'].find_one(filter):
            messages.error(request, "Group name already exists.")
            return redirect("groupcreate")

        group_info = {'group_name': group_name, 'member': member, 'memberNum': membernum, 'description': description, 'private': private}
        print(group_info)
        status, inserted_id = create_a_group('chat', 'group', group_info)
        if status:
            print('new group saved to db successfully ====>', inserted_id)
        else:
            print('saving to group db failed')

        user_filter = {'user_name': username}
        # add the new group to the group list of the group creater
        MONGO_CLIENT['chat']['friend'].update_one(user_filter, {'$push': {'group_list': group_name}}) 

    return render(request, 'chat/groupcreate.html', {})


'''
•	Search by group name
Use a whole group name or a partial keyword to search for a group. (Partial) Matched public group results will be shown.
•	Search by group ID
Use a group ID to search for a group. Matched group (public or private) result will be shown.
•	Search by friend ID
Use a friend ID to search for a friend. Matched friend result will be shown.
'''
def groupsearch(request):
    username = ''
    if request.user.is_authenticated:
        username = request.user
        username = str(username)
    else:
        return redirect("/auth/signin")
    group_name = request.POST["groupname"]
    search_by = request.POST.get('search_type')
    res_group_list = []
    #print(search_by)
    print(type(group_name))
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
                #dict = {'group_name': record['group_name'], 'description': record['description']}
                res_group_list.append(record['group_name'])

    elif search_by == 'private_group': # search by id, matched result will be returned
        if len(group_name) != 24 or not all(c in string.hexdigits for c in group_name):
            pass
        else:
            myquery = {'_id': ObjectId(group_name)}
            result = MONGO_CLIENT['chat']['group'].find(myquery)
            added_group_list = user_record[0]['group_list']
            for record in result:
                #dict = {'group_name': record['group_name'], 'description': record['description']}
                res_group_list.append(record['group_name'])

    else:
        if len(group_name) != 24 or not all(c in string.hexdigits for c in group_name):
            pass
        else:
            myquery = {'_id': ObjectId(group_name)} # friend id
            result = MONGO_CLIENT['chat']['friend'].find(myquery)
            added_group_list = user_record[0]['friend_list'] # added friend list
            for record in result:
                print(record)
                #dict = {'group_name': record['user_name'], 'description': ''}
                res_group_list.append(record['user_name']) # matched user

    unadded_group_list = [i for i in res_group_list if i not in added_group_list]
    result_group_list = []

    for i in unadded_group_list:
        if search_by == 'friend':
            myquery = {'_id': ObjectId(group_name)}
            result = MONGO_CLIENT['chat']['friend'].find(myquery)
            for record in result:
                print(record)
                dict = {'group_name': i, 'description': ''}
                result_group_list.append(dict)
        else:
            myquery = {'group_name': i}
            result = MONGO_CLIENT['chat']['group'].find(myquery)
            added_group_list = user_record[0]['group_list']
            for record in result:
                dict = {'group_name': i, 'description': record['description']}
                result_group_list.append(dict)

    print(result_group_list)
    return render(request, 'chat/groupadd.html', {
        'search_by': search_by,
        'res_group_list': result_group_list
    })


'''
When the user enters the chat page, his/her group list and friend list will be shown. 
If the user enters a group/friend chat, the chat history will be returned. 
The group name comes from the URL. To prevent the case that the user tries to enter a 
chatroom not belonging to him/her by changing the URL, this function will also check 
whether the group/friend belongs to the user, and send an attack indicator to frontend.
'''
def groupchat(request, room_name):
    room_name_with_type = room_name
    type = room_name[:1]
    room_name = room_name[1:]
    print(type)
    print('inside room view ======>', room_name)
    group_name = room_name
    username = ''
    if request.user.is_authenticated:
        username = request.user
        username = str(username)
    else:
        return redirect("/auth/signin")
    if not username:
        return HttpResponseRedirect('homepage/login/')

    if type == 'g':
        filters = {'group_name': group_name}
        sort_fields = [('time', -1)]
        previous_messages = []
        for chat in MONGO_CLIENT['chat']['chat_message'].find(filters).sort(sort_fields).limit(20):
            print(chat)
            chat['_id'] = str(chat['_id'])
            chat['sender'] = str(chat['sender'])
            chat['time'] = chat['time']
            chat['message'] = chat['message']
            previous_messages.append(chat)
        previous_messages = sorted(previous_messages, key=lambda s: s['time'])

    if type == 'f':
        group_name = username + '&' + room_name
        try_filter = {'group_name': group_name}
        if MONGO_CLIENT['chat']['friend_chat'].find_one(try_filter):
            pass
        else:
            group_name = room_name + '&' + username
        print("friend chat name: {}".format(group_name))
        filters = {'group_name': group_name}
        sort_fields = [('time', -1)]
        previous_messages = []
        for chat in MONGO_CLIENT['chat']['chat_message'].find(filters).sort(sort_fields).limit(20):
            print(chat)
            chat['_id'] = str(chat['_id'])
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
        img_filter = {'user_name': chat['sender']}
        img_record = MONGO_CLIENT['chat']['friend'].find_one(img_filter)
        image = img_record['profile']
        chat['image'] = image


    filter = {'user_name': username}
    result = MONGO_CLIENT['chat']['friend'].find(filter)
    friend_list_tmp = result[0]['friend_list']
    group_list = result[0]['group_list']
    print("user: {}, friend list: {}, group list: {}".format(username, friend_list_tmp, group_list))
    friend_list = []

    for friend in friend_list_tmp:
        fri_filter = {'user_name': friend}
        fri_record = MONGO_CLIENT['chat']['friend'].find_one(fri_filter)
        dict = {"username": friend, 'image': fri_record['profile']}
        friend_list.append(dict)
        
    print('-----------friend list----', friend_list)
    print('previous_messages =======>', previous_messages)
    if room_name_with_type == 'groupchat':
        room_name_with_type = 'g' + room_name_with_type

    attack_indicator = 0
    print(room_name_with_type[1:])
    if group_name not in group_list and room_name_with_type[1:] not in friend_list_tmp and group_name != 'roupchat':
        previous_messages = []
        attack_indicator = 1

    if group_name == 'roupchat':
        attack_indicator = 0

    return render(request, 'chat/groupchat.html', {
        'room_name': room_name_with_type,
        'friend_list': friend_list,
        'group_list': group_list,
        'prev_messages': previous_messages,
        'current_user': username,
        'history_indicator': 0,
        'attack_indicator': attack_indicator
    })


def friendadd(request):
    if request.method == "POST":
        friend_name = request.POST["friendname"]
    username = ''
    if request.user.is_authenticated:
        username = request.user
        username = str(username)
        add_a_friend('chat', 'friend', username, friend_name)
    else:
        return redirect("/auth/signin")
        
    return render(request, 'chat/groupadd.html', {})


'''
This function will return the group list and friend list (together with their profile photo) of the current user. 
'''
def grouplist(request):
    username = ''
    if request.user.is_authenticated:
        username = request.user
        username = str(username)
    else:
        return redirect("/auth/signin")
    print(type(str(username)))
    username = str(username)
    filter = {'user_name': username}
    user_record = MONGO_CLIENT['chat']['friend'].find(filter)
    print(user_record)
    group_list = user_record[0]['group_list']
    friend_list = user_record[0]['friend_list']
    group = []
    for i in range(len(group_list)):
        tmp = MONGO_CLIENT['chat']['group'].find({"group_name": group_list[i]})
        id = tmp[0]['_id']
        memberNum = tmp[0]['memberNum']
        dict = {"group_name": group_list[i], "group_id": str(id), "mumberNum": memberNum}
        group.append(dict)   
    print(group)

    friend = []
    for i in range(len(friend_list)):
        tmp = MONGO_CLIENT['chat']['friend'].find({"user_name": friend_list[i]})
        id = tmp[0]['_id']
        image = tmp[0]['profile']
        dict = {"friend_name": friend_list[i], "friend_id": str(id), 'image': image}
        friend.append(dict)
    print(friend)

    return render(request, 'chat/grouplist.html', {
        'group_list': group,
        'friend_list': friend,
        'current_user': username
    })


'''
After the user entering a searching keyword, all the (partial) matched previous 
chat messages of the current group will be returned as a list.
'''
def historysearch(request,room_name,keyword=None):
    username = ''
    if request.user.is_authenticated:
        username = request.user
        username = str(username)
    else:
        return redirect("/auth/signin")

    group_name_with_type = room_name
    group_name = group_name_with_type[1:]
    type = group_name_with_type[:1]

    if type == 'f':
        group_name = username + '&' + group_name
        try_filter = {'group_name': group_name}
        if MONGO_CLIENT['chat']['friend_chat'].find_one(try_filter):
            pass
        else:
            group_name = group_name + '&' + username
        print("friend chat name: {}".format(group_name))
    
    message_list = []
    if keyword != None:
        print("roomname: "+ group_name+ "  keyword: "+keyword)
        #group_name = 'CSCI_3100'
        #keyword = 'i'
        filter_kwd = { "message": { "$regex": ".*" + keyword + ".*" } }
        msg_result = MONGO_CLIENT['chat']['chat_message'].find(filter_kwd)

        for record in msg_result:
            if record['group_name'] == group_name:
                timestamp = record['time']
                day = timestamp.day
                month = timestamp.month
                year = timestamp.year
                hour = timestamp.hour
                minute = timestamp.minute
                time = str(day) + '/' + str(month) + '/' + str(year) + ' ' + str(hour).zfill(2) + ':' + str(minute).zfill(2)
                dict = {
                    'message_id': str(record['_id']),
                    'sender': record['sender'],
                    'time': time,
                    'message': record['message']
                }
                message_list.append(dict)
    print(message_list)

    filters = {'group_name': group_name}
    sort_fields = [('time', -1)]
    previous_messages = []
    for chat in MONGO_CLIENT['chat']['chat_message'].find(filters).sort(sort_fields).limit(20):
        print(chat)
        chat['_id'] = str(chat['_id'])
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
        img_filter = {'user_name': chat['sender']}
        img_record = MONGO_CLIENT['chat']['friend'].find_one(img_filter)
        image = img_record['profile']
        chat['image'] = image


    filter = {'user_name': username}
    result = MONGO_CLIENT['chat']['friend'].find(filter)
    friend_list_tmp = result[0]['friend_list']
    group_list = result[0]['group_list']
    print("user: {}, friend list: {}, group list: {}".format(username, friend_list_tmp, group_list))
    friend_list = []

    for friend in friend_list_tmp:
        fri_filter = {'user_name': friend}
        fri_record = MONGO_CLIENT['chat']['friend'].find_one(fri_filter)
        dict = {"username": friend, 'image': fri_record['profile']}
        friend_list.append(dict)

    attack_indicator = 0
    if group_name not in group_list and group_name_with_type[1:] not in friend_list_tmp and group_name != 'roupchat':
        previous_messages = []
        message_list = []
        attack_indicator = 1

    if group_name == 'roupchat':
        attack_indicator = 0

    return render(request, 'chat/groupchatsearch.html', {
        'history': message_list,
        'history_indicator': 1,
        'room_name': room_name,
        'friend_list': friend_list,
        'group_list': group_list,
        'prev_messages': previous_messages,
        'current_user': username,
        'attack_indicator': attack_indicator
    })

