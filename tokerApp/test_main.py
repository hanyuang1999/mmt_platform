#!/usr/bin/env python
import pytest
import os
import datetime
import time
import re
import xlwt
import xlrd
import configparser

class Dispose_ini():
    def __init__(self, filepath):
        self.config = configparser.ConfigParser()  # 实例化解析对象  
        self.filepath = filepath

    def get_value(self,sec,opt):
        self.config.read(self.filepath, encoding='utf-8')
        value = self.config.get(sec,opt)
        return value

    def set_value(self,sec,opt,value):
        self.config.read(self.filepath, encoding='utf-8')
        self.config.set(sec, opt, value)
        self.config.write(open(self.filepath, "w", encoding="utf-8"))

class Excel():
    def __init__(self,filepath) -> None:
        self.filepath = filepath
    def createsheet(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        sheet = workbook.add_sheet("测试记录")
        return sheet,workbook
    def getrecord(self):
        if os.path.exists(self.filepath):
          data= xlrd.open_workbook(self.filepath) 
          testtable = data.sheet_by_name("测试记录") 
          testrecord = []
          for i in range(1,testtable.nrows):
              testrecord.append(testtable.row_values(i))
        else:
          testrecord = []
        return testrecord
    def writetitle(self,sheet):
        stylecase=xlwt.XFStyle()
        fontcase=xlwt.Font() 
        fontcase.bold = True
        stylecase.font = fontcase
        sheet.write(0,0,"测试时间",stylecase)
        sheet.write(0,1,"序列号",stylecase)
        sheet.write(0,2,"测试结果",stylecase)
        sheet.write(0,3,"详细测试记录",stylecase)
    def writerecord(self,sheet,testrecord):
        record = self.getrecord()
        self.writetitle(sheet)
        record.append(testrecord)
        row = 1
        for i in record:
            sheet.write(row, 0, str(i[0])) 
            sheet.write(row, 1, str(i[1]))
            sheet.write(row, 2, str(i[2])) 
            sheet.write(row, 3, str(i[3])) 
            row += 1       
    def saveExcel(self,workbook):
        workbook.save(self.filepath)

def get_codepath():
    return "/sensorhub_web_toker/web_toker/tokerApp/"

def get_testtitle():
    codepath=get_codepath()
    inifile = Dispose_ini(os.path.join(codepath,"SH_info.ini"))
    resultname = inifile.get_value('SH','SH_SN') +'_'+inifile.get_value('SH','TestTime')
    return resultname

def writeExcellog(filepath,testrecord):
    logfile = Excel(filepath)
    sheet,workbook = logfile.createsheet()
    logfile.writerecord(sheet,testrecord)
    logfile.saveExcel(workbook)

def shortinfo(info):
    shortinfo = ''
    commandoutput = info.read()
    try:
        shorttext = commandoutput.split("=========================== short test summary info ============================")[1].strip("\n")
        shortlines = shorttext.split("\n")
        resulttext = shortlines.pop()
        if "error" in resulttext:#先处理error错误
            result = "error"
        else:
            result = "failed"
        for i in shortlines:
            shortinfo = shortinfo + i.split(' - ')[0] + '\n'
    except:
        pattern = re.compile(r"scripts\/.*?PASSED",re.M) 
        shortlines = pattern.findall(commandoutput)
        result = "passed"
        for i in shortlines:
            shortinfo = shortinfo + i + '\n'
    return shortinfo,result


if __name__ == '__main__':
    codepath = get_codepath()
    TestTime= datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    inifile = Dispose_ini(os.path.join(codepath,"SH_info.ini"))
    inifile.set_value('SH','TestTime',TestTime)
    inifile.set_value('SH','running_status','True')
    SH_SN = inifile.get_value('SH','SH_SN')
    test_type = inifile.get_value('SH','test_type')
    TestTitle = get_testtitle()
    TestDay = str(datetime.date.today())
    resultpath =os.path.join(TestDay,TestTitle)
    os.chdir("/sensorhub_web_toker/web_toker/templates")
    if test_type!="0":
        TestResult= os.popen('pytest ./testcase -vs -k \"%s\" --alluredir=./resultLog/%s/%s'%(test_type,TestDay,TestTitle))
    else:
        TestResult= os.popen('pytest ./testcase -vs --alluredir=./resultLog/%s/%s'%(TestDay,TestTitle))
    SH_info,SH_result=shortinfo(TestResult)
    SH_info = SH_info.strip()
    os.popen("allure generate ./resultLog/%s -o ./result/%s --clean" %(resultpath,resultpath))
    inifile.set_value('SH','testresult','Success')
    time.sleep(5)
    inifile.set_value('SH','running_status','False')



