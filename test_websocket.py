import asyncio
import json
import websockets


async def test_websocket():
    uri = "ws://127.0.0.1:8000/queue/1"

    async with websockets.connect(uri) as websocket:
        message = await websocket.recv()
        print("Connected:", message)

        print("Waiting for appointment events...")

        while True:
            message = await websocket.recv()
            print("Received event:", json.loads(message))


asyncio.run(test_websocket())