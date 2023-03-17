import os
import sys
CURRENT_DIR = os.path.split(os.path.abspath(__file__))[0]  # 当前目录
config_path = CURRENT_DIR.rsplit('/', 1)[0]  # 上一级目录
sys.path.append(config_path)
print(config_path)
from toker_BLL.toker_BLL import usr_manager

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

from bs4 import BeautifulSoup
from configparser import ConfigParser
from configparser import ConfigParser
import os


class My_Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)


    def do_POST(self):
        self.send_response(200)
        usr_manager.set_res({'result': 'HTTP SERVER OK'})

        datas = self.rfile.read(int(self.headers['content-length']))
        print('headers', self.headers)
        print("-->> post:", self.path, self.client_address)
        # print(json.loads(str(datas,'utf-8'))["SN"])
        print(json.loads(str(datas,'utf-8'))['SN'])

        usr_manager.set_target_ini_item('SH', 'sh_sn', '"'+json.loads(str(datas,'utf-8'))["SN"]+'"')
 

        usr_manager.target_exe_start("python3 ./Sensorhub_Test/scripts/main.py")
        time.sleep(1)

     
        # os.popen("python Sensorhub_Test/scripts/main.py")

        # print("succccccccccccccccccccc")

        # config.read("./Sensorhub_Test/SH_info.ini",encoding="utf-8")
 

        # value1 = config.get("SH",'running_status') 
      


        while (usr_manager.get_target_ini_item("SH",'running_status')=='True'):
             print("target running")
             time.sleep(1)
        
        
        


    
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        
        self.end_headers()

        
        print(usr_manager.get_target_ini_item("SH",'testresult'))
        usr_manager.set_res({'testresult':usr_manager.get_target_ini_item("SH",'testresult')})

        self.wfile.write(json.dumps(usr_manager.get_res()).encode())

        'python3 main.py'


def toker_init(target_path,ini_path,host,port):
    usr_manager.set_target_path(target_path)
    usr_manager.set_ini_path(ini_path)
    usr_manager.set_addr(host,port)

if __name__ == '__main__':
    toker_init("./Sensorhub_Test","./Sensorhub_Test/SH_info.ini",'0.0.0.0',19999)
    print(usr_manager.get_target_ini_item("SH",'testresult'))
    
   
   
    server = HTTPServer(usr_manager.get_addr(), My_Server)
    print("server启动@ : %s:%s" % usr_manager.get_addr())
    server.serve_forever()


