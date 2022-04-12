import datetime
import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, JsonWebsocketConsumer, WebsocketConsumer

from csci3100.settings import MONGO_CLIENT

def save_to_database(db, collection, chat_message):
    print('inside save_to_database====>', db, collection, chat_message)
    r = MONGO_CLIENT[db][collection].insert_one(chat_message)
    return True, r.inserted_id


def find_image(username):
    filter = {'user_name': username}
    img_record = MONGO_CLIENT['chat']['friend'].find_one(filter)
    image = img_record['profile']
    return image


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print("self room name: {}".format(self.room_name))
        #self.room_group_name = 'chat_%s' % self.room_name
        self.room_group_name = self.room_name[1:]
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['username']

        timestamp = datetime.datetime.now()
        group_name = self.scope['url_route']['kwargs']['room_name']
        print("In websocket receive: {}".format(group_name))
        type = group_name[:1]
        group_name = group_name[1:]

        if type == 'g':
            pass
        else: # type == 'f'
            try_name = sender + '&' + group_name
            filter = {"group_name": try_name}
            if MONGO_CLIENT['chat']['friend_chat'].find_one(filter):
                #print("------find: {}".format(MONGO_CLIENT['chat']['friend_chat'].find_one(filter)))
                group_name = try_name
            else:
                group_name = group_name + '&' + sender
                #print("------{}------".format(group_name))
        
        #sender = event['username']
        chat_data = {'group_name': group_name, 'sender': sender, 'time': timestamp, 'message': message}
        status, inserted_id = save_to_database('chat', 'chat_message', chat_data)
        day = timestamp.day
        month = timestamp.month
        year = timestamp.year
        hour = timestamp.hour
        minute = timestamp.minute
        time = str(day) + '/' + str(month) + '/' + str(year) + ' ' + str(hour).zfill(2) + ':' + str(minute).zfill(2)
        # Send message to WebSocket
        chat_data['_id'] = str(chat_data['_id'])
        chat_data['time'] = time
        chat_data['image'] = find_image(sender)

        # Send message to room group
        print("self.room_group_name: {}, chat message: {}".format(self.room_group_name, chat_data))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': chat_data
            }
        )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        print("In websocket chat_message: {}".format(event))
        print("message in func chat_message: {}".format(message))
        await self.send(text_data=json.dumps({
            'message': message
        }))

