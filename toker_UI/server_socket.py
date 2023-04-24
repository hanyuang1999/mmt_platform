import asyncio
from websockets.server import serve

async def server(websocket, path):
    print("New connection:", websocket.remote_address)
    try:
        async for message in websocket:
            print("Received message from", websocket.remote_address, ":", message)
            if(message=="unique confirm"):
                clients.add(websocket)
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
    async with serve(server, "localhost", 7777):
        print("server start...")
        await asyncio.Future()  # run forever

asyncio.run(main())