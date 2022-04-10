import datetime
import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, JsonWebsocketConsumer, WebsocketConsumer

from csci3100.settings import MONGO_CLIENT

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

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
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

'''
@database_sync_to_async
def save_to_database(db, collection, chat_message):
    print('inside save_to_database====>', db, collection, chat_message)
    r = MONGO_CLIENT[db][collection].insert_one(chat_message)
    return True, r.inserted_id


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('inside ChatConsumer connect()')
        self.username = self.scope['session'].get('username', 'server')
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # for multicast
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        # for broadcast
        # await self.channel_layer.group_add('server_announcements', self.channel_name)
        await self.accept()
        chat_data = {'username': self.username, 'online': True, 'type': 'chat_message'}
        await self.channel_layer.group_send(self.room_group_name, chat_data)


    async def disconnect(self, close_code):
        print('inside ChatConsumer disconnect()')
        # send offline broadcast
        offline_data = {'username': self.username, 'online': False, 'type': 'offline'}
        await self.channel_layer.group_send(self.room_group_name, offline_data)
        # await self.channel_layer.group_discard('server_announcements', self.channel_name)
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # Receive message from WebSocket
    async def receive(self, text_data=None):
        print('inside ChatConsumer receive()')
        # if not self.username == 'server':
        #     username = self.scope['session']['username']
        # else:
        #     username = 'server'
        text_data_json = json.loads(text_data)
        username = text_data_json['username']
        timestamp = text_data_json.get('timestamp') or ''
        online = text_data_json.get('online', True)
        chat_data = {'type': 'chat_message', 'username': username, 'timestamp': timestamp}
        message = text_data_json.get('message', '')
        if message:
            chat_data.update({'message': message})
        await self.channel_layer.group_send(self.room_group_name, chat_data)


    async def chat_message(self, event):
        print('inside ChatConsumer chat_message()', event)
        await self.send(text_data=json.dumps(event))
        # save to database
        message = event.get('message') or ''
        if message:
            user_name = event['username']
            room_name = self.scope['url_route']['kwargs']['room_name']
            timestamp = datetime.datetime.utcnow()
            chat_data = {'group_name': room_name, 'sender': user_name, 'time': timestamp, 'message': {'text': message}}
            status, inserted_id = await save_to_database('chat', 'chat_message', chat_data)
            if status:
                print('chat saved to db successfully ====>', inserted_id)
            else:
                print('saving to db failed')


    async def offline(self, event):
        print('inside offline() ====>', event)
        await self.send(text_data=json.dumps(event))
'''
