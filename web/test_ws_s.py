import asyncio
import websockets

# WebSocket 服务器配置
WS_HOST = '0.0.0.0'
WS_PORT = 5006

async def websocket_handler(websocket):
    print(f"New WebSocket connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await websocket.send("Message received")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print(f"WebSocket connection closed for {websocket.remote_address}")

async def start_websocket_server():
    async with websockets.serve(websocket_handler, WS_HOST, WS_PORT):
        print(f"WebSocket server started on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()  # 保持服务器运行

if __name__ == "__main__":
    asyncio.run(start_websocket_server())