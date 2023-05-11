import subprocess
import threading
import re

folder_ip = ""

def server1():
    global folder_ip
    command = "allure open ./Sensorhub_Test/result"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
        line = process.stdout.readline()
        print(line)
        if "Server started at" in line:
            print(line)
            line = line.strip()
            break
    print(line)
    pattern = r"http://127.0.0.1:(\d+)/"
    match = re.search(pattern, line)
    if match:
        folder_ip = match.group(1)
        print(folder_ip)
    else:
        print("端口未找到")

def server2():
    global folder_ip
    while True:
        if folder_ip:
            print(folder_ip)
            break

t1 = threading.Thread(target=server1)
t2 = threading.Thread(target=server2)
t1.start()
t2.start()
t1.join()
t2.join()