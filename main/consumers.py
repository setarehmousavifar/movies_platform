"""Channels consumers for breaking catalog alerts."""

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BreakingAlertConsumer(AsyncJsonWebsocketConsumer):
    group_name = 'breaking_alerts'

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def breaking_message(self, event):
        await self.send_json(event.get('payload', {}))
