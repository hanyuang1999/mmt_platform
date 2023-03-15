import os
import sys
CURRENT_DIR = os.path.split(os.path.abspath(__file__))[0]  # 当前目录
config_path = CURRENT_DIR.rsplit('/', 1)[0]  # 上一级目录
sys.path.append(config_path)
print(config_path)
from toker_DAL.toker_DAL import usr_service

class Usr_manager:
    def __init__(self):
       print("BLL suc")

    def set_addr(self,host,port):  
        usr_service.set_addr(host,port)
        
    def set_recive(self,recive):
        usr_service.set_recive(recive)
        
    def set_ini_path(self,ini_path):
       usr_service.set_ini_path(ini_path)

    def set_res(self,res):
        usr_service.set_res(res)
       

    def set_target_path(self,target_path):
        usr_service.set_target_path(target_path)
    
    def get_addr(self):
        
       
        return usr_service.get_addr()
       
    def get_recive(self):
        return  usr_service.get_recive()
       
    def get_res(self):
        return  usr_service.get_res()
    
    def get_target_path(self):
        return usr_service.get_target_path()
    
    def get_ini_path(self):
        return usr_service.get_ini_path()

    
    def get_target_ini_item(self,session,item):
        return usr_service.get_target_ini_item(session,item)

    def set_target_ini_item(self,session,item,value):
        usr_service.set_target_ini_item(session,item,value)
        pass
    def target_exe_start(self,cmd):
         usr_service.target_exe_start(cmd)
usr_manager=Usr_manager()
        