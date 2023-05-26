import subprocess
import re
import os
import signal

def signal_handler(sig, frame):
    for p in processes:
        p.send_signal(signal.SIGINT)  # 使用 send_signal() 发送 SIGINT
    for p in processes:
        p.wait()
    print("已成功杀死所有子进程。")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

processes = []
try:
    if not os.path.exists("./Sensorhub_Test/result"):
        os.makedirs("./Sensorhub_Test/result")
    command = "allure open ./Sensorhub_Test/result"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True,start_new_session=False)
    
    while True:
        line = process.stdout.readline()
        if "Server started at" in line:
            line = line.strip()
            print(line)
            break

    pattern = r'(?<=:)\d+(?=/)'
    match = re.search(pattern, line)
    if match:
        result_port = match.group()
        with open("tmp_port.txt", "w") as f:
            f.write(str(result_port))
    else:
        print("端口未找到")
    while True:
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            # 继续等待过程结束或收到 KeyboardInterrupt
            pass
except KeyboardInterrupt:
    print("接收到键盘中断，正在终止子进程...")

