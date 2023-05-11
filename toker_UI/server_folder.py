import subprocess
import re

command = "allure open ./Sensorhub_Test/result"
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True,start_new_session=True)
try:
    while True:
        line = process.stdout.readline()
        if "Server started at" in line:
            line = line.strip()
            print(line)
            break
except KeyboardInterrupt:
    process.terminate()
    process.wait()
    raise
pattern = r'(?<=:)\d+(?=/)'
match = re.search(pattern, line)
if match:
    result_port = match.group()
    with open("tmp_port.txt", "w") as f:
        f.write(str(result_port))
else:
    print("端口未找到")
process.wait()

