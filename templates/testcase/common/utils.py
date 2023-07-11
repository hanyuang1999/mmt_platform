#!/usr/bin/env python
import os
import xlwt
import xlrd
import configparser

codepath=os.path.abspath(os.path.join(os.path.dirname(__file__),"../../../tokerApp"))
filepath=os.path.join(codepath,'SH_info.ini')

def get_codepath():
    #获取Sensorhub_Test的基本路径
    codepath=os.path.abspath(os.path.join(os.path.dirname(__file__),"../../../tokerApp"))
    return codepath
def get_testtitle():
    codepath=get_codepath()
    inifile = Dispose_ini(os.path.join(codepath,"SH_info.ini"))
    resultname = inifile.get_value('SH','SH_SN') +'_'+inifile.get_value('SH','TestTime')
    return resultname

class Dispose_ini():
    def __init__(self, filepath):
        self.config = configparser.ConfigParser()  # 实例化解析对象
        self.config.read(filepath, encoding='utf-8')  
        self.filepath = filepath

    def get_value(self,sec,opt):
        value = self.config.get(sec,opt)
        # with open(filepath,'r',encoding='utf-8') as f:
        #     testtitle=f.readline()
        return value
    def set_value(self,sec,opt,value):
        self.config.set(sec, opt, value)
        with open(self.filepath, 'w') as fp:
            self.config.write(fp)       

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

    









if __name__=='__main__':
    pass

