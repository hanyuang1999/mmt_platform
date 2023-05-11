import asyncio
from websockets.server import serve
import subprocess
import threading

folder_ip = ""

def server1():
    global folder_ip
    command = "allure open ./Sensorhub_Test/result"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
    while True:
        line = process.stdout.readline()
        if "Server started at" in line:
            line = line.strip()
            break
    pattern = r"http://127.0.0.1:(\d+)/"
    match = re.search(pattern, line)
    if match:
        folder_ip = match.group(1)
        print(folder_ip)
    else:
        print("端口未找到")
    process.wait()

async def server2_work(websocket, path):
    global folder_ip
    print("New connection:", websocket.remote_address)
    try:
        async for message in websocket:
            print("Received message from", websocket.remote_address, ":", message)
            if(message=="unique confirm"):
                clients.add(websocket)
                wrapped_string = {"folder_ip": folder_ip}
                json_string = json.dumps(wrapped_string)
                await send_to_html(json_string)
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
async def server2():
    async with serve(server2_work, "0.0.0.0", 19799):
        print("server start...")
        await asyncio.Future()  # run forever

asyncio.run(main())