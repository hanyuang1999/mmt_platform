import os
import sys
import subprocess
from threading import Thread
import signal
CURRENT_DIR = os.path.split(os.path.abspath(__file__))[0]  # 当前目录
config_path = CURRENT_DIR.rsplit('/', 1)[0]  # 上一级目录
sys.path.append(config_path)
print(config_path)
from toker_BLL.toker_BLL import usr_manager

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
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
        if(json.loads(str(datas,'utf-8'))['SN']=="terminateAll"):
            usr_manager.set_target_ini_item('SH', 'running_status', 'False')
            
        else:
            usr_manager.set_target_ini_item('SH', 'sh_sn', '"'+json.loads(str(datas,'utf-8'))["SN"]+'"')
            usr_manager.set_target_ini_item('SH', 'test_type', '"'+json.loads(str(datas,'utf-8'))["TestType"]+'"')
    

            command='python3 ./Sensorhub_Test/scripts/main.py'
            usr_manager.set_target_ini_item('SH', 'running_status', 'True')
            process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,preexec_fn=os.setsid)
            def run_long_command(command, process):
                while (usr_manager.get_target_ini_item("SH",'running_status')=='True'):
                    pass
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                print("target finish")
                
            command_runner = Thread(target=run_long_command, args=(command, process))
            command_runner.start()
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            print(usr_manager.get_target_ini_item("SH",'testresult'))
            usr_manager.set_res({'testresult':usr_manager.get_target_ini_item("SH",'testresult')})
            self.wfile.write(json.dumps(usr_manager.get_res()).encode())
            
            
            



def toker_init(target_path,ini_path,host,port):
    usr_manager.set_target_path(target_path)
    usr_manager.set_ini_path(ini_path)
    usr_manager.set_addr(host,port)

if __name__ == '__main__':
    toker_init("./Sensorhub_Test","./Sensorhub_Test/SH_info.ini",'0.0.0.0',29799)
    print(usr_manager.get_target_ini_item("SH",'testresult'))
    
   
   
    server = ThreadingHTTPServer(usr_manager.get_addr(), My_Server)
    print("server启动@ : %s:%s" % usr_manager.get_addr())
    server.serve_forever()


