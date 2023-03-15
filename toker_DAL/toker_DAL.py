import os
import sys
CURRENT_DIR = os.path.split(os.path.abspath(__file__))[0]  # 当前目录
config_path = CURRENT_DIR.rsplit('/', 1)[0]  # 上一级目录
sys.path.append(config_path)
print(config_path)
from toker_MODEL.toker_model import user_models
from configparser import ConfigParser
from configparser import ConfigParser
import os


class Usr_service:
    def __init__(self)->None:
       print("dal suc")
       self.config=ConfigParser()
    
    def set_addr(self,host,port):  
        user_models.host=host
        user_models.port=port
        pass

    def set_recive(self,recive):
        user_models.recive=recive
    def set_ini_path(self,ini_path):
        user_models.ini_path=ini_path

    def set_res(self,res):
        user_models.res=res

    def set_target_path(self,target_path):
        user_models.target_path=target_path
    
    def get_addr(self):
        
        
        return user_models.host,user_models.port
       
    def get_recive(self):
        return  user_models.recive
       
    def get_res(self):
        return  user_models.res
    
    def get_target_path(self):
        return user_models.target_path
    
    def get_ini_path(self):
        return user_models.ini_path

    
    def get_target_ini_item(self,session,item):
      
        self.config.read(self.get_ini_path(),encoding="utf-8")
        _ = self.config.get(session,item) 
        return _

    def set_target_ini_item(self,session,item,value):
        self.config.read(self.get_ini_path(),encoding="utf-8")
        self.config.set(session, item, value) 
        self.config.write(open(self.get_ini_path(), "r+", encoding="utf-8"))
        print("ini set OK")
        pass
    def target_exe_start(self,cmd):
         os.popen(cmd)


usr_service=Usr_service()
        