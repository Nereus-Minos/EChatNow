from channels.generic.websocket import AsyncWebsocketConsumer
import json
from mvc.models import Chatmessage,User

# 异步写法
class ChatConsumer(AsyncWebsocketConsumer):
    '''
    //部分代码解释
    self.scope['url']['kwargs']['room_name']：通过解包url获取传入的关键词的信息，对于每一个consumer实例而言，都拥有一个scope，在这个scope中包含了此次连接的信息，包含url的位置以及关键词
    self.room_group_name = 'chat_%s'%self.room_name：使用用户的房间名称直接命名组名称，不进行转义
    async_to_sync(self.channel_layer.group_add)(...)：1、加入一个组中；2、async_to_sync 这个装饰器是必须的因为chatconsumer是一个同步websocket连接，但是对于channel layer需要调用异步方法，因为所有的channel layer都需要异步实现；3、组名字仅限于ASCII字母数字和字符句点
    self.accept()：接受websocket连接，如果该方法并非在connect()中被调用，则会发生拒绝并关闭连接
    async_to_sync(self.channel_layer.group_discard)(...)：关闭组
    async_to_sync(self.channel_layer.group_send)：1、发送一个event到组；2、在这个event中一般会定义的第一个key:value组为type，value锁指向的就是调用的方法

    '''
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        group_chat = self.room_name.split('_')[1] + self.room_name.split('_')[2]
        self.room_group_name = 'chat_%s' % group_chat

        _user2friend = self.room_name.split('_')[0]
        if _user2friend == 'yes':
            self._user_id = self.room_name.split('_')[1]
            self._friend_id = self.room_name.split('_')[2]
        else:
            self._friend_id = self.room_name.split('_')[1]
            self._user_id = self.room_name.split('_')[2]

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # 连接上后将消息列表放到聊天界面
        message = self.read_mysql_chat_message()

        await self.send(text_data=json.dumps({
            'is_read_mysql': 'yes',
            'message': message,
        }))



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
        _write_id = text_data_json['own']

        _chatmessage = Chatmessage(message=message, write_id=_write_id,
                                   user_id=self._user_id, friend_id=self._friend_id)
        _chatmessage.save()

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'write_id': _write_id,
            }
        )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        write_id = event['write_id']

        if int(write_id) == int(self._user_id):
            _is_write = True
        else:
            _is_write = False

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'is_read_mysql': 'no',
            'is_write': _is_write,
        }))


    def read_mysql_chat_message(self):
        try:
            # 多个过滤器逐个调用表示逻辑与关系，同sql语句中where部分的and关键字。
            from django.db.models import Q
            message = [[messageall.write_id == int(self._user_id), messageall.message] for messageall in
                       Chatmessage.objects.filter(Q(Q(user_id=self._user_id) & Q(friend_id=self._friend_id)) |
                                                  Q(Q(friend_id=self._user_id) & Q(user_id=self._friend_id)))
                           .filter(user_id__in=[self._user_id, self._friend_id])]
        except:
            message = '数据库查询错误'
        return message