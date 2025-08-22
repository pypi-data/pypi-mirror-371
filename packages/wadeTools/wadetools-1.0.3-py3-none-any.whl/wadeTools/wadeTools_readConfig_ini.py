#!/usr/bin/env python
# coding=utf-8
"""
使用方法：

Ini_Data = ReadConfig('config.ini')
"""
import configparser
import os
from wadeTools import wadeTools_log
from wadeTools.wadeTools_Print import wadePrint
my_logger = wadeTools_log.my_logger
class ReadConfig:
    """定义一个读取配置文件的类"""

    def __init__(self, filepath="filepath"):
        root_dir = os.path.dirname(os.path.abspath('.'))
        # self.configpath = os.path.join(root_dir, f"{filepath}")
        self.configpath = os.path.join(os.getcwd(), filepath)

        self.cf = configparser.RawConfigParser()
        try:self.cf.read(self.configpath,encoding='utf-8')
        except UnicodeDecodeError as e:
            my_logger.error(f"XXXXXXX:程序已停止，请将读取的文本编码转为UTF-8。错误编码的文件是:{os.path.join(os.getcwd(),filepath)}，\n   {e}")
            exit()
    # self.cf.read(configpath,encoding='utf-8')
    def getFilepath(self):
        return self.configpath
    def get_param(self, title,param):
        try:
            value = self.cf.get(title, param)
            return value
        except Exception as e:
            wadePrint(e)
            return ""


    def setItem(self, title, key, val):  #修改内容
        """
        :param title: USER  ini显示是[USER]
        :param key:   key    ：abc = 666
        :param val:   value  666   ：abc = 666
        :return:
        """
        try:
            self.cf[title]
        except:
            self.cf.add_section(title)

        if title == '' or key == '':
            return False
        self.cf[title][key] = val
        return True

    def saveIni(self,real_path='config.ini'):  #保存修改
        """

        :param real_path: xxx.ini
        :return:
        """
        # root_dir = os.path.dirname(os.path.abspath('.'))
        # self.configpath = os.path.join(root_dir, real_path)
        self.configpath = os.path.join(os.getcwd(), real_path)

        for title in self.cf:
            for key in self.cf[title]:
                self.cf.set(title, key, self.cf[title][key])
        self.cf.write(open(self.configpath,"w",encoding='utf-8'))

if __name__ == '__main__':

    #绝对路径
    Ini_Data = ReadConfig('config.ini')
    runNumNow = Ini_Data.get_param('USER', "【中】")
    Ini_Data.setItem('USER',"【中】",[123,34])  #修改
    Ini_Data.saveIni('config.ini')  #保存
    wadePrint(runNumNow)

