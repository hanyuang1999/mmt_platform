import asyncio
from websockets.server import serve
import sys
import json

async def server(websocket, path):
    print("New connection:", websocket.remote_address)
    try:
        async for message in websocket:
            print("Received message from", websocket.remote_address, ":", message)
            if(message=="unique confirm"):
                clients.add(websocket)
                with open('./templates/tmp_port.txt', 'r') as f:
                    result_port = int(f.read().strip())
                data = {"result_port": result_port}
                port_message = json.dumps(data)
                await send_to_html(port_message)
            else:
                await send_to_html(message)
    finally:
        print("Connection closed:", websocket.remote_address)

async def send_to_html(message):
    for client in clients.copy():
        try:
            await client.send(message)
        except Exception as e:
            print("Error sending to", client.remote_address, ":", e)
            clients.remove(client)

clients = set()

async def main():
    async with serve(server, "0.0.0.0", 19799):
        print("server start...")
        await asyncio.Future()  # run forever

asyncio.run(main())