import asyncio
import websockets
from typing import List

clients: List[websockets.WebSocketServerProtocol] = []

async def handle_connection(websocket, path):
    async for message in websocket:
        # Логирование входящего сообщения
        print(f"Получено сообщение от клиента: {message}")
        # Пример ответа клиенту
        await websocket.send(f"Вы сказали: {message}")

async def main_socket():
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # run forever

