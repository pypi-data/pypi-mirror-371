#!/usr/bin/env python
# coding=utf-8
# author:wade
# contact: 317909531@qq.com
# datetime:2021/12/5 22:14
#requests.head(url).headers 可以在请求之前获取服务器需要的提交类型

"""
文件说明：
geiUrl函数，传入链接，获取内容

wade_Request_get  和geturl一个意思，加入了新的功能

def wade_Request_get(url,cookie,addHeader=dict):
    url：传入链接
    addHeader：是需要的内容更新进请求header中，默认的host自动化解析


def retryRequest(func)
    重连问题解决

def get_Request_JsFiles(htmlText)
    传入html.text，匹配到js列表返回


# requests库中的params参数用于向URL添加查询字符串，data参数用于向请求体添加表单数据（如POST请求），而json参数用于向请求体添加JSON数据。具体来说:
# params：将参数以键值对形式附加到URL的查询字符串中，常用于GET请求。
# data：以字典或元组列表的形式提供表单数据，发送POST请求时使用，Content-Type为application/x-www-form-urlencoded。
# json：以字典或任何可序列化的对象提供JSON数据，发送POST请求时使用，Content-Type为application/json。
# 总的来说，params和data都是向请求添加参数的方式，但data主要用于传递表单数据，而json则用于传递结构化的数据。
#   :param url: 请求地址
#   :param method: 请求方法，默认为 GET
#   :param headers: 请求头信息，默认为 None  headers = {'User-Agent': 'Mozilla/5.0'}  r = requests.get('https://httpbin.org/get', headers=headers)
#   :param params: URL 参数，默认为 None     payload = {'key1': 'value1', 'key2': 'value2'}   r = requests.get('https://httpbin.org/get', params=payload)
#   :param data: 发送的数据。通常用于POST请求,默认为 None payload = {'key1': 'value1', 'key2': 'value2'} response = requests.post(url, data=payload)
#   :param json: JSON 数据，默认为 None payload = {'key1': 'value1', 'key2': 'value2'} response = requests.post(url, json=payload)
#   :param cookies: Cookie 信息，默认为 None  cookies = {'name': 'value'}  response = requests.get(url, cookies=cookies)
#   :param files: 上传的文件，默认为 None files = {'file': open('test.txt', 'rb')} response = requests.post(url, files=files)
#   :param proxies: 代理信息，默认为 None  proxies = {'http': 'http://127.0.0.1:8888', 'https': 'http://127.0.0.1:8888'}  response = requests.get(url, proxies=proxies)
#   :param verify: SSL证书验证，默认为 None  response = requests.get(url, verify=False)
# 禁用证书验证
r = requests.get('https://httpbin.org/get', verify=False)

# 使用证书验证
r = requests.get('https://httpbin.org/get', cert=('path/to/cert.pem', 'path/to/key.pem'))
#   :return: 响应对象
"""
import random
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests import Timeout, ConnectTimeout
from requests.exceptions import InvalidProxyURL, ProxyError, MissingSchema, ReadTimeout, SSLError
from wadeTools import wadeTools_error
#这个可以解决重连的问题，用他做装饰器就可以了（装饰器）

HEADERS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 QuarkPC/4.2.5.446"]

def retryRequest(func):
    RETRIES = 1# 重试的次数
    count = {"num": RETRIES}

    def wrapped(*args, **kwargs):
        try:
            # print(count['num'])
            return func(*args, **kwargs)
        except (SSLError,ProxyError,ReadTimeout,Timeout,ConnectionError,ConnectTimeout):  # (SSL链接错误，被拉黑/请求格式错/代理超时)代理成功,代理连接不上URL，1、url错误  2 url没反应 ，但通过代理访问的URL出问题,可能是url错误，可能是被服务器拉黑无任何反应
            if count['num'] == 1:
                 print('本地ip请求不成功，再试一次',count['num'])
                 count['num'] += 1
            elif count['num'] <= 10:
                 print('代理请求不成功，切换新的代理',count['num'])
                 # kwargs['proxies'] = wadeTools_Agent.getAGENT()
                 count['num'] += 1
            else:
                raise wadeTools_error.Error_break("使用代理10次访问仍然出现问题，请检查url后再运行")

            return wrapped(*args, **kwargs)
    return wrapped
#这个可以解决重连的问题，用他做装饰器就可以了（范例函数）

def myRequest():
    print("haha")
    url= 'http://www.tbzhu1.com'
    session = requests.session()
    html = session.get(url)
    print(html.url)
    # if html.url == 'http://www.tbzhu.com/':  #可以根据判断来辨别是否是自己想要得结果，不是的话也可以重连
    #     raise Exception


def wade_Request_get(url,addHeader=dict,proxies=None,timeout=10):   #proxies 默认是不用写得
    from urllib.parse import urlparse  # 正则url标准库

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
    # print(headers)
    if proxies:
        html = requests.get(url, headers=headers,proxies=proxies,timeout= timeout)
    else:
        html = requests.get(url, headers=headers,timeout= timeout)
    return html

def wade_Request_get_byParams(url,addHeader=dict,params=None):
    from urllib.parse import urlparse  # 正则url标准库

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
    # print(headers)
    html = requests.get(url, headers=headers,params=params)
    return html

@retryRequest
def wade_Request_post(url,addHeader=dict,data=dict):
    from urllib.parse import urlparse  # 正则url标准库

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
    #print(headers)
    html = requests.post(url, headers=headers,data=data)
    return html
@retryRequest
def wade_Request_post_CSRF(url,addHeader=dict,data=dict):
    from urllib.parse import urlparse  # 正则url标准库
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
    #print(headers)
    html = requests.post(url, headers=headers,data=data)
    return html

def get_Request_JsFiles(htmlText):
    # 获取网页中包含的所有js网址，目的是为了抓js中的内容
    patternjs1 = '<script src="(.*?)"'
    patternjs2 = '<script type="text/javascript" src="(.*?)"'
    list = re.compile(patternjs1, re.S).findall(htmlText)
    list += re.compile(patternjs2, re.S).findall(htmlText)
    # print(list)
    return list


def getheaders(s):  #格式化header,可以把复制的header直接变成格式化后的来用，从Accept: */*开始复制
    ls = s.split('\n')
    lsl = []
    ls = ls[1:-1]
    headers = {}
    for l in ls:
        l = l.split(': ')
        lsl.append(l)

    for x in lsl:
        headers[str(x[0]).strip('    ')] = x[1]
    print(headers)
    return headers
@retryRequest
def geiUrl(url):
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

    # 采用正则，抓tbk链接
    # url = f"https://question.jd.com/question/getQuestionAnswerList.action?callback=jQuery8364807&page=2&productId"
    # 采用正则，抓tbk链接
    match = re.compile(r'''//(\S*\.["com"|"cn"|"com.cn"]+)''')
    result = match.findall(url)
    # print(abc[0])
    if not result: #如果没有找到url，报错
        print('url的格式不对，函数停止')
        return
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': random.choice(HEADERS),
        'Connection': 'keep-alive',
        'Host': f"{result[0]}",
        'Content-Type': 'application/json'
    }
    print(headers)
    html = requests.get(url,headers = headers)
    print(html.headers)
    return html
@retryRequest
def bookInfo(url):  #抓笔记本数据
    # 采用正则，抓tbk链接
    html = geiUrl(url)
    print('--------请求中-----------')
    # print(html.text)
    print('---------开始格式化html，加载beautifulSoup------------')
    soup = BeautifulSoup(html.text,'lxml')  # html为html源代码字符串，type(html) == str
    # print(soup.prettify())   #美化输出 格式化html
    print('---------开始清洗数据------------')

    pdData_dict={}
    pdData_dict["name"] = soup.h3.text

    for tr_s in soup.table.children:  #判断如果子节点的兄弟节点不存在的话，直接跳过
        if tr_s.next_element.next_sibling== None:
            continue
        # print(tr_s.next_element.next_element)
        if (tr_s.next_element.next_element.name == 'span' or tr_s.next_element.next_element.name == 'b') and tr_s.next_element.next_sibling.name == "td":
            pdData_dict[f'{tr_s.next_element.next_element.string}'] = [tr_s.next_element.next_sibling.string]
    print(pdData_dict)

    df_new = pd.DataFrame(pdData_dict)
    return df_new,pdData_dict["name"]
if __name__ == '__main__':
    # url = f"https://detail.zol.com.cn/param_copy_1343674_blue_2_0_560.html"
    from threading import Thread

    import requests


    proxies = {
        "http": '',
        "https": ''
    }


    def changeAgent():
        global proxies
        url = 'https://proxy.qg.net/allocate?Key=9XFOUQ5B&Num=1&AreaId=&DataFormat=txt&DataSeparator=%5Cr%5Cn&Detail=0'
        html = requests.get(url, timeout=10)
        print('切换新代理：', html.text)
        key = '9XFOUQ5B'
        passwd = '2F5079EA8A6B'
        proxy = f'http://{key}:{passwd}@{html.text}'

        proxies = {
            "http": proxy,
            "https": proxy
        }
        return proxies


    def getAgent():
        global proxies
        # if proxies["http"]=="" and proxies["https"]=="":
        #     changeAgent()
        print(proxies)
        return proxies


    def changeAgentButton():  # 默认直接显示

        sg.theme('DarkAmber')  # 设置当前主题色
        # 界面布局，将会按照列表顺序从上往下依次排列，二级列表中，从左往右依此排列
        layout = [[sg.B("切换代理", key="切换代理")]]

        def my_long_operation():
            print("点击按钮")
            changeAgent()

        # 创造窗口
        windows = sg.Window('代理窗口', layout, location=(0, 0), font=("宋体", 10))

        while True:
            event, values = windows.Read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                print('代理窗口关闭')
                break
            if event == '切换代理':  # 登录按钮
                windows.perform_long_operation(my_long_operation, '-finish-')

        windows.close()


    # proxies= {'http': 'http://9XFOUQ5B:2F5079EA8A6B@117.91.61.202:26745', 'https': 'http://9XFOUQ5B:2F5079EA8A6B@117.91.61.202:26745'}
    changeAgent()
    url = f"http://www.youtube.com"

    # html = wade_Request_get(url=url,addHeader={})
    # # print(html.text)
    # print(requests.head(url).headers)
    # print(requests.head(url).headers['Content-Type'])
    # print(type(requests.head(url).headers))
    # a = requests.get("http://www.youtube.com")
    # print(a.text)
    a = requests.get(url,proxies=getAgent())
    print(a.status_code)
    print(a.text)




    # df_new,new_name = bookInfo(url)  #返回抓到的数据
    # # df_new.to_csv(path_or_buf='产品清单.csv',index=False)
    # # print("======================")
    #
    # try:
    #     df_readData = pd.read_csv("产品清单.csv", encoding="gbk")
    #     print(df_readData)
    # except:
    #     df_new.to_csv(path_or_buf='产品清单.csv',index=False,encoding="gbk")
    #     df_readData = pd.read_csv("产品清单.csv", encoding="gbk")
    #     print("======================")
    #
    # if not find_needData(df_readData,"name",new_name):
    #     # 合并DataFrame 数据
    #     resule = pd.concat([df_readData, df_new], join='outer', sort=True)
    #     resule.to_csv(path_or_buf='产品清单.csv', index=False,encoding="gbk")
    #     print(f"成功加入一条数据 {new_name}")
    # else:
    #     print("已存在")


















