#!/usr/bin/env python
import pytest
import os
from scripts.common import utils
import datetime
import time
import re


def writeExcellog(filepath,testrecord):
    logfile = utils.Excel(filepath)
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
    codepath=utils.get_codepath()
    TestTime= datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    inifile = utils.Dispose_ini(os.path.join(codepath,"SH_info.ini"))
    inifile.set_value('SH','TestTime',TestTime)
    inifile.set_value('SH','running_status','True')
    SH_SN = inifile.get_value('SH','SH_SN')
    test_type = inifile.get_value('SH','test_type')
    TestTitle = utils.get_testtitle()
    TestDay = str(datetime.date.today())
    os.chdir(codepath)

    if test_type!="0":
        TestResult= os.popen('pytest /sensorhub_web_toker/web_toker/templates/testcase -k \"%s\" --alluredir=./SHlog/%s/%s'%(test_type,TestDay,TestTitle))
    else:
        TestResult= os.popen('pytest /sensorhub_web_toker/web_toker/templates/testcase --alluredir=./SHlog/%s/%s'%(TestDay,TestTitle))
    SH_info,SH_result=shortinfo(TestResult)
    SH_info = SH_info.strip()
    Excellogpath = os.path.join(codepath,'result/'+ TestDay + "/测试报告.xls")
    time.sleep(1)
    writeExcellog(Excellogpath,[TestTime,SH_SN,SH_result,SH_info])
    inifile.set_value('SH','running_status','False')


    



