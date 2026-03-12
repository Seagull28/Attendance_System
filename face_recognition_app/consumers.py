from channels.generic.websocket import AsyncWebsocketConsumer
import json

class StudentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.student_id = self.scope['url_route']['kwargs']['student_id']
        self.group_name = f'student_{self.student_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def attendance_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'attendance.update',
            'roll_number': event['roll_number'],
            'subject': event['subject'],
            'status': event['status'],
            'timestamp': event['timestamp']
        }))
