#!/usr/bin/env python
import paramiko
import os
from loguru import logger
class SshConnectError(Exception):
    pass
class ControlHost():
    def __init__(self,host,username,passward,port=22) -> None:
        self.host = host
        self.username = username
        self.passward = passward     
        self.ssh = ControlHost.__sshConn(self.host,self.username,self.passward)
        #logger.debug(self.ssh)
        if type(self.ssh) == str:
            self.status = False
        else:
           self.status = True
           self.sftp =self.__sftpConn()
    def close(self):
        if hasattr(self.ssh,'close'):
            self.ssh.close()
    
    @staticmethod#创建静态连接方法
    def __sshConn(host,username,passward):
        ssh =paramiko.SSHClient()#创建SSH客户端对象
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=host,username=username,password=passward,timeout=15)
        except:
            return 'SSH Connect Error'
            #raise SshConnectError("SSH Connect %s Error!" %host)
        else:
            return ssh
    
    def __sftpConn(self):
        transport =self.ssh.get_transport()#1.先ssh连上，2.再建立通道 这个步骤的目的是获取原来建立的ssh对象
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp
    def exeCommand(self,cmd,timeout=500):
        _, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
        try:
            channel = stdout.channel
            exit_code = channel.recv_exit_status()
            stdout = str(stdout.read(),encoding="utf-8").strip()
            stderr = str(stderr.read(),encoding="utf-8").strip()
            return {'status':1,'stdout':stdout,'stderr':stderr,'exit_code':exit_code}
        except:
            return {'status':0,'stdout':stdout,'stderr':stderr,'exit_code':127}
        
    def sftpFile(self,localpath,remotepath,action):
        #实现文件的上传下载
        try:
            if action == "push":
                dirname = os.path.dirname(remotepath)
                self.exeCommand("mkdir -p %s" % dirname)
                self.sftp.put(localpath,remotepath)
                return {'status':1,'message':'sftp %s %s success!' %(self.host,action)}
            elif action == 'pull':
                dirname = os.path.dirname(localpath)
                if not os.path.exists(dirname):
                    os.mkdir(dirname)
                #print(dirname)
                self.sftp.get(remotepath,localpath)
                return {'status':1,'stdout message':'sftp %s %s success!' %(self.host,action),"stderr": ""}
        except Exception as e:
            return {'status':0,'stderr message':'sftp %s %s fail!' %(self.host,action,str(e)),"stdput": ""}

