import asyncio

message_queue = asyncio.Queue()

async def notify_clients(data):
    await message_queue.put(data) 