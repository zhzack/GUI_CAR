import asyncio
import websockets

async def test_websocket():
    async with websockets.connect("ws://localhost:5006") as websocket:
        await websocket.send("Hello, server!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.run(test_websocket())