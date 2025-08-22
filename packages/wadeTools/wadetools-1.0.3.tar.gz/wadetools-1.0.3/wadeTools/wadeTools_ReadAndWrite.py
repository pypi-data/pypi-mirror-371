#!/usr/bin/env python
#coding=utf-8
# author:wade
# contact: 317909531@qq.com
# datetime:2022/4/5 22:14
import re
"""
文件说明：

---------------------------文件读写----------------------------
文件的读写：保存文件，读取文件列表
wadeRead  # ('web.data','rb')   读,返回字典列表
    dir: 相对路径和文件名 例'web.data'
    writeType: 例'rb' 等写入类型 string
wadeSave  # ('wade.data','wb',[])   保存列表不如保存成dict，可以保存很多内容
    dir: 相对路径和文件名 例'web.data'
    readType: 例'wb' 等写入类型 string
    dataList: 存储的内容 list

---------------------------保存日志----------------------------
#读取日志,返回列表类型  写死日志文件：'运行日志.log'
readLog()    #读取日志，文件不存在自动创建
saveLog(msg) #（'我是日志内容'）  保存日志到文件,自动创建

---------------------------下载文件----------------------------
文件和文件夹的操作函数（读写/下载）
wadeDownloadFile ：下载网络图片/视频,不显示进度，自己写请求，
    filePath: 'movie'
    fileName: 1.jpg 1.mp3 .1.exe
    html: html = request.get(xxx)
wadeDownLoadStreamFile :下载网络图片/视频，FilePath文件路径  1.jpg  movie/1.jpg  c:/1.jpg  1.mp4
    filePath: 'movie'
    fileName: 1.jpg 1.mp3 .1.exe
    html: html = request.get(xxx)
wadeDownLoadStreamFileByUrl ：直接填写url，显示进度，请求函数里已实现
    filePath: 'movie'
    fileName: 1.jpg 1.mp3 .1.exe
    url: 'www.baidu.com/1.exe'


wadeDownLoadStreamFileByUrl_AddHeader： 可以动态添加header的临时属性
    filePath: 'movie'
    fileName: 1.jpg 1.mp3 .1.exe
    url: 'www.baidu.com/1.exe'

----快捷代码------
append 续写  read 是读  write是写
import wadeTools_ReadAndWrite
wadePrint(wadeTools_ReadAndWrite.wadeRead('wade.data', 'rb'))
wadeTools_ReadAndWrite.wadeSave('wade.data','wb',[1,2])

"""
import os
import pickle
import random
import time
import re
import traceback
import requests
from wadeTools import wadeTools_log
from wadeTools.wadeTools_Print import wadePrint,wadeRedPrint
my_logger = wadeTools_log.my_logger

import json
class wadeSetObject:
    """
    集合扩展类，支持读取 load， 单条增add ， 列表增updata，删remove查query
    """
    def __init__(self, filename):
        self.filename = filename
        self.data = set()
        self.load()

    def add(self, item):
        self.data.add(item)
        self.save()
    def updateList(self, item:list):
        self.data.update(item)
        self.save()

    def remove(self, item):
        if item in self.data:
            self.data.remove(item)
            self.save()
        else:
            wadePrint(f"删除的 {item} 在文件列表中不存在，忽略")

    def query(self, item):
        return item in self.data

    def load(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.data = set(json.load(file))
        except FileNotFoundError:
            self.save()
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.data = set(json.load(file))
    def save(self):
        with open(self.filename, 'w',encoding='utf8') as file:
            json.dump(list(self.data), file)
class wadeTextObject:
    """
    txt扩展类支持读取 load， 单条增add ， 列表增updata，删remove查query
    """
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.load()

    def load(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.data = [line.strip() for line in file]  # 读取每一行并删除前后的空白字符
        except FileNotFoundError:
            self.save()
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.data = [line.strip() for line in file]  # 读取每一行并删除前后的空白字符

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            for line in self.data:
                file.write(line + '\n')  # 在每条文本后添加换行符

    def add(self, text):
        self.data.append(text)
        self.save()

    def remove(self, text):
        if text in self.data:
            self.data.remove(text)
            self.save()

    def search(self, text):
        return text in self.data
    def getListByText_form_Sign(self,text):
        """
        getListByText_form_Sign load，约定分隔符为这个符号@---@
        把txt通过约定的标记拆分为列表返回
        """


        # 输入字符串
        # input_str = "你好@----@你好发@----@发发@----@发的"
        # 使用正则表达式来分割字符串
        # '@----@' 是我们要分割的标记
        # 使用 re.split() 函数来根据这个标记分割字符串
        resultList = re.split('@----@', text)
        # 输出结果
        try:  # 去除空字符
            resultList.remove("")
        except:
            pass
        return resultList
    def clear(self):
        self.data.clear()  # 清空self.data列表
        self.save()  # 保存清空后的内容到文件


def delSpecialName(STR):  #过滤掉windows文件不支持的字符串
    """
    过滤掉windows文件不支持的字符串
    :param STR: 待过滤的文本
    :return:
    """
    for i,j in ("/／","\\＼","?？","|︱","\"＂","*＊","<＜",">＞"):
        STR=STR.replace(i,j)
    return STR


def lunxunTxt(filepath):
    """
    随机返回文本的一行：返回值为str类型
    :param filepath: 传入文件相对路径或者绝对路径：./1.txt  c:/1.txt
    :return:列表
    """
    needList = readText(filepath)
    if needList==[]:
        return ""
    return str(random.choice(readText(filepath)))

def readText(filepath):
    """
    读取文本：每行读取为列表
    :param filepath: 传入文件相对路径或者绝对路径：./1.txt  c:/1.txt
    :return:列表
    """
    textlist = []
    try:

        for line in open(f'{filepath}',encoding='utf-8'):
            # 清洗空格后如果不为空就下一步处理
            if line.strip() != '':
                # my_logger.debug(f"本行内容为{line}")
                # 每行的数据都需要清洗空格后进行下一步处理
                abc = line.strip()
                textlist.append(abc)
            else:
                my_logger.debug("删除空行")
    except FileNotFoundError as e:
        # 找不到文件则新建,路径必须保证没错，否则也报错
        with open(f'{filepath}', 'w+', encoding='utf-8') as f:
            my_logger.debug(e,f"{filepath}不存在，自动新建")
    except UnicodeDecodeError as e:
        my_logger.error(f"！！！:程序已停止，请将读取的文本编码转为UTF-8，如果是GBK也会出错,错误编码文件:{filepath}，\n   {e}")
        exit()
    return textlist


def writeList_to_TXT(filename,list):
    # 重新保存txt，不存在则自动创建
    with open(f'{filename}','w+',encoding='utf8') as f:
        for i in list:
            f.write(f"{i.strip()}"+'\r')



def additem_to_Txt(filename,itemStr):
    # 续写txt，不存在则自动创建
    with open(f'{filename}','a+',encoding='utf8') as f:
        f.write(f"{itemStr.strip()}"+'\r')


def getInputBianliangName(BianLiang):
    # 获取变量的名字 的字符串
    stack = traceback.extract_stack()
    filename, lineno, function_name, code = stack[-2]
    vars_name = re.compile(r'\((.*?)\).*$').search(code).groups()[0]
    name = vars_name.replace('self.', '')
    wadePrint(name)
    return name

#保存列表不如保存成dict，可以保存很多内容
def wadeSave(dir,readType,dataDict:dict):  #返回的是字典
    """
    ('wade.data','wb',[])

    :param dir: 相对路径和文件名 例'web.data'
    :param readType: 例'wb' 等写入类型 string
    :param dataDict: 存储的内容 list
    :return:None
    """
    with open(dir,readType) as f:
        pickle.dump(dataDict, f)


#向已经生成的字典中添加项目
def wadeSave_AddItem(dir,readType,dataDict:dict):  #返回的是字典
    """
    写操作用：wb
    :param dir: 文件
    :param readType: wb 写入
    :param dataDict: 存的数据
    :return: None
    """
    if os.path.exists(dir):#存在该文件
        itemDict = wadeRead(dir,'rb')
        itemDict.update(dataDict)
        # ('wade.data','wb',[])
        # dir: 相对路径和文件名 例'web.data'
        # readType: 例'wb' 等写入类型 string
        # dataList: 存储的内容 list
        with open(dir,readType) as f:
            pickle.dump(itemDict, f)
    else:#不存在该文件
        my_logger.debug("创建新文件，条目加入成功")
        # wadePrint(dataDict)
        wadeSave(dir,"wb",dataDict)
#读,返回字典列表
import os
import pickle

def wadeRead(dir, writeType, Encoding='utf-8'):
    """
    读操作~用：rb
    :param dir: 文件路径和名称
    :param writeType: 读写模式（如 'rb', 'wb', 'r', 'w' 等）
    :param Encoding: 文件的编码，默认为 utf-8（只在文本模式下有效）
    :return: 读取到的内容，可能是字典或空字典
    """
    try:
        if os.path.exists(dir):  # 如果文件存在
            if 'b' in writeType:  # 如果是二进制模式
                with open(dir, writeType) as f:
                    dataDict = pickle.load(f)
            else:  # 如果是文本模式
                with open(dir, writeType, encoding=Encoding) as f:
                    dataDict = f.read()
            return dataDict
        else:  # 如果文件不存在
            wadeSave(dir, "wb", {})  # 使用二进制写入创建新文件
            my_logger.debug(f"创建新文件 {dir}")
            return {}
    except Exception as e:
        wadePrint(e)
        return {}

def wadeReadHtml(dir, writeType, Encoding='utf-8'):
        """
        读取HTML文件内容，并返回文件内容作为字符串
        :param dir: 文件路径和名称
        :param writeType: 读写模式（如 'r' 或 'rb' 等）
        :param Encoding: 文件的编码，默认为 utf-8（只在文本模式下有效）
        :return: HTML 文件内容或空字符串
        """
        try:
            if os.path.exists(dir):  # 如果文件存在
                if 'b' in writeType:  # 二进制模式，读取字节数据
                    with open(dir, writeType) as f:
                        content = f.read()
                else:  # 文本模式，读取文本数据
                    with open(dir, writeType, encoding=Encoding) as f:
                        content = f.read()
                return content  # 返回 HTML 文件的文本内容
            else:  # 如果文件不存在
                my_logger.debug(f"文件 {dir} 不存在")
                return ''
        except Exception as e:
            wadePrint(f"读取文件 {dir} 时发生错误：{e}")
            return ''

def get_current_time():
    from datetime import datetime
    current_time =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # current_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    return current_time

# 保存日志
def saveLog(msg):
    log_file_write = open("运行日志.log", mode='a', encoding='utf-8')
    log_file_write.writelines(f'{get_current_time()}:{msg}')

#读取日志,返回列表类型
def readLog():
    try:
        return open('运行日志.log', mode='r', encoding='utf-8').read().splitlines()
    except IOError as e:
        saveLog('日志文件Start')
        return []
def wadeDownLoadImage(filePath,fileName,url):
    # 下载图片
    # url = "https://example.com/image.jpg"
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(os.path.join(filePath,fileName), "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

def wadeDownloadFile(filePath,fileName,html):
    '''FilePath文件路径  FileName:文件名  html: html = request.get(xxx) ,请求自己写'''
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    with open(os.path.join(filePath,fileName),'wb') as f:
        f.write(html.content)
        f.close()
def wadeDownLoadStreamFile(filePath,fileName,html):  #显示进度，html 是requests请求返回对象
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    length = float(html.headers['content-length'])
    count = 0
    count_tmp = 0
    time1 = time.time()
    with open(os.path.join(filePath,fileName),'wb') as f:
        for streamData in html.iter_content(chunk_size=1024*8):
            if streamData:
                f.write(streamData)
                count += len(streamData)
                if time.time() - time1 > 0.5:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 1024 / 2
                    count_tmp = count
                    wadePrint(f"\r下载状态{fileName} 进度:{'{:.2f}'.format(p)}%  Speed: {'{:.2f}'.format(speed)}M/S",end='')
                    time1 = time.time()
        f.close()
def wadeDownLoadStreamFileByUrl_AddHeader(filePath,fileName,url,addHeader=dict):  #显示进度，直接写了下载地址,附加了头文件，可以动态加入cookie
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    from urllib.parse import urlparse  # 正则url标准库

    HEADERS = [
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        'Mozilla/5.0 (Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
        'Mozilla/5.0 (Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
        'Mozilla/5.0 (Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Mozilla/5.0 (Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.27 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/601.1.27',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    ]
    headers = {
        'Accept': '*/*',
        # 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': random.choice(HEADERS),
        'Connection': 'keep-alive',
        'Host': f"{urlparse(url).netloc}",
        'Content-Type': 'application/json',
        # 'Cookie': cookie
    }
    if addHeader:
        headers.update(addHeader)
    wadePrint(headers)
    html = requests.get(url, headers=headers,stream=True)
    length = float(html.headers['content-length'])
    count = 0
    count_tmp = 0
    time1 = time.time()
    with open(os.path.join(filePath,fileName),'wb') as f:
        for streamData in html.iter_content(chunk_size=1024*8):
            if streamData:
                f.write(streamData)
                count += len(streamData)
                if time.time() - time1 > 0.5:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 1024 / 2
                    count_tmp = count
                    wadePrint(f"\r下载状态{fileName} 进度:{'{:.2f}'.format(p)}%  Speed: {'{:.2f}'.format(speed)}M/S",end='')
                    time1 = time.time()
        f.close()
def wadeDownLoadStreamFileByUrl(filePath,fileName,url):  #显示进度，直接写了下载地址

    if not os.path.exists(filePath):
        os.makedirs(filePath)
    html = requests.get(url,stream=True)
    length = float(html.headers['content-length'])
    count = 0
    count_tmp = 0
    time1 = time.time()
    with open(os.path.join(filePath,fileName),'wb') as f:
        for streamData in html.iter_content(chunk_size=1024*8):
            if streamData:
                f.write(streamData)
                count += len(streamData)
                if time.time() - time1 > 0.5:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 1024 / 2
                    count_tmp = count

                    time1 = time.time()
                    try:
                        from wadeTools import wadeTools_gol
                        gol=wadeTools_gol.Singletion()

                        gol.windows['jindu'].update(f"\r下载状态{fileName} 进度:{'{:.2f}'.format(p)}%  Speed: {'{:.2f}'.format(speed)}M/S")
                    except Exception as e:
                        # wadePrint(e)
                        wadePrint(f"\r下载状态{fileName} 进度:{'{:.2f}'.format(p)}%  Speed: {'{:.2f}'.format(speed)}M/S", end='')
                        pass
        f.close()

if __name__ == '__main__':

    #读写
    # additem_to_Txt('111.txt',[3,4])

    # wadePrint(lunxunTxt('111.txt'))
    # wadePrint(wadeRead('wade.data', 'rb'))
    # wadeSave_AddItem('wade.data',"wb",{"123":123})
    # wadeSave_AddItem('wade.data','wb',{'123':23})
    # abc =123
    # getInputBianliangName(abc)
    #
    # #日志
    # saveLog('123')
    #
    # #下载
    # wadeDownLoadStreamFileByUrl('1', '360.exe', 'http://down.360safe.com/setup.exe')
    # wadeDownLoadImage('.','222222.jpg','https://img-home.csdnimg.cn/images/20230921025407.png')
    title='4171539-九牧大力神家用马桶（11173-2-1/31KB-3）最新评测，销量说明一切-九牧（JOMOO）11173-2-1/31KB-3大力神.h'
    itle_for_filename = title.replace('/', '、')  # 将 / 替换为 _
    print(itle_for_filename)
    title='./未发布内容/4171539-九牧大力神家用马桶（11173-2-1、31KB-3）最新评测，销量说明一切-九牧（JOMOO）11173-2-1/31KB-3大力神.html'
    writeList_to_TXT(title,'fdfdf')
    pass






