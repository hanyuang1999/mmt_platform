import os
import datetime

# 获取当前时间
now = datetime.datetime.now()

# 生成文件名
filename = now.strftime("%Y-%m-%d_%H-%M-%S.txt")

# 获取当前工作目录
#current_dir = os.getcwd()
current_dir = "/root/xhd/web_toker_django/tokerApp/Sensorhub_Test/gen_files"

# 拼接完整的文件路径
file_path = os.path.join(current_dir, filename)

# 创建并打开新文件
with open(file_path, 'w') as new_file:
    # 写入内容
    new_file.write(f"{filename}\n")
    
    
