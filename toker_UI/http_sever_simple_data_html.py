from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

from bs4 import BeautifulSoup
from configparser import ConfigParser
from configparser import ConfigParser
import os


config=ConfigParser()


data = {'result': 'HTTP SERVER OK'}
host = ('0.0.0.0', 19999)


class My_Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)


    def do_POST(self):
        self.send_response(200)

        datas = self.rfile.read(int(self.headers['content-length']))
        print('headers', self.headers)
        print("-->> post:", self.path, self.client_address)
        print(str(datas,'utf-8'))
        config.read("./Sensorhub_Test/SH_info.ini",encoding="utf-8")
 


        config.set('SH', 'sh_sn', '"'+json.loads(str(datas,'utf-8'))["SN"]+'"') 
        config.write(open("./Sensorhub_Test/SH_info.ini", "r+", encoding="utf-8"))
        
     
        # os.popen("python Sensorhub_Test/scripts/main.py")

        # print("succccccccccccccccccccc")

        # config.read("./Sensorhub_Test/SH_info.ini",encoding="utf-8")
 

        # value1 = config.get("SH",'running_status') 
      


        # while (value1=='True'):
        #     print("target running")
        #     time.sleep(10)
        
        
        


    
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        
        self.end_headers()
       
        value2 = config.get("SH",'testresult') 
        print(value2)
        data["testresult"]=value2



        self.wfile.write(json.dumps(data).encode())

        'python3 main.py'



if __name__ == '__main__':
    server = HTTPServer(host, My_Server)
    print("server启动@ : %s:%s" % host)

    server.serve_forever()
