# -*- coding: UTF-8 -*-
import http.client
import urllib.parse
import http.client
import urllib.parse
import urllib.request
import json
from aliyunsdkcore.client import AcsClient #阿里云核心代码库 安装方法：pip install aliyun-python-sdk-core-v3
from aliyunsdkcore.request import CommonRequest #阿里云官方核心代码库

"""
文字转语音的api，wordToVolic(text) 可以直接用
"""
def wordToVolice(text):
    """
    文字输出为音频
    :param text:需要转换的文字
    :return: 直接输出mp3
    """
    appKey = 'Afmo70O9f2sovWOH'
    uID = 'LTAI4GCaEY7V4Cigqxpgg1mV'
    uKEY = 'iR3WppxVLSd5BPx58WeAy5PA0r5g0h'
    text = f'{text}'
    voice = 'dahu'  # 发音人
    saveName = 'good.mp3'
    volume = 100
    makeMp3(appKey, uID, uKEY, text, voice, saveName, volume)



## 获取token值
def get_token(uID,uKEY):
    # 创建AcsClient实例
    client = AcsClient(
        uID,  # 为阿里云后台创建的 accesskey id
        uKEY,  # 为阿里云后天创建的  accesskey secret
        "cn-shanghai"
    )
    # 创建request，并设置参数
    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    request.set_version('2019-02-28')
    request.set_action_name('CreateToken')
    response = client.do_action_with_exception(request)
    token_result = eval(response.decode('utf-8'))
    token_result = token_result['Token']['Id']
    #print(token_result)
    return token_result

# @wadeTools_Request.retryRequest
def processGETRequest(appKey, token, text, audioSaveFile, format, sampleRate,voice,volume) :
    host = 'nls-gateway.cn-shanghai.aliyuncs.com'
    url = 'https://' + host + '/stream/v1/tts'
    # 设置URL请求参数
    url = url + '?appkey=' + appKey
    url = url + '&token=' + token
    url = url + '&text=' + text
    url = url + '&format=' + format
    url = url + '&sample_rate=' + str(sampleRate)
    url = url + '&voice=' + str(voice)
    url = url + '&voice=' + str(volume)
    # voice 发音人，可选，默认是xiaoyun。
    # url = url + '&voice=' + 'xiaoyun'
    # volume 音量，范围是0~100，可选，默认50。
    # url = url + '&volume=' + str(50)
    # speech_rate 语速，范围是-500~500，可选，默认是0。
    # url = url + '&speech_rate=' + str(0)
    # pitch_rate 语调，范围是-500~500，可选，默认是0。
    # url = url + '&pitch_rate=' + str(0)
    print(url)
    # Python 2.x请使用httplib。
    # conn = httplib.HTTPSConnection(host)
    # Python 3.x请使用http.client。
    conn = http.client.HTTPSConnection(host)
    conn.request(method='GET', url=url)
    # 处理服务端返回的响应。
    response = conn.getresponse()
    print('Response status and response reason:')
    print(response.status ,response.reason)
    contentType = response.getheader('Content-Type')
    print(contentType)
    body = response.read()
    if 'audio/mpeg' == contentType :
        with open(audioSaveFile, mode='wb') as f:
            f.write(body)
        print('The GET request succeed!')
    else :
        print('The GET request failed: ' + str(body),'等待2秒钟后重试')
        raise Exception  #呼叫装饰器，让他重连
    conn.close()
def processPOSTRequest(appKey, token, text, audioSaveFile, format, sampleRate) :
    host = 'nls-gateway.cn-shanghai.aliyuncs.com'
    url = 'https://' + host + '/stream/v1/tts'
    # 设置HTTPS Headers。
    httpHeaders = {
        'Content-Type': 'application/json'
        }
    # 设置HTTPS Body。
    body = {'appkey': appKey, 'token': token, 'text': text, 'format': format, 'sample_rate': sampleRate}
    body = json.dumps(body)
    print('The POST request body content: ' + body)
    # Python 2.x请使用httplib。
    # conn = httplib.HTTPSConnection(host)
    # Python 3.x请使用http.client。
    conn = http.client.HTTPSConnection(host)
    conn.request(method='POST', url=url, body=body, headers=httpHeaders)
    # 处理服务端返回的响应。
    response = conn.getresponse()
    print('Response status and response reason:')
    print(response.status ,response.reason)
    contentType = response.getheader('Content-Type')
    print(contentType)
    body = response.read()
    if 'audio/mpeg' == contentType :
        with open(audioSaveFile, mode='wb') as f:
            f.write(body)
        print('The POST request succeed!')
    else :
        print('The POST request failed: ' + str(body))
    conn.close()


def makeMp3(appKey,uID,uKEY,text,voice,saveName,volume):
    # appKey = 'Afmo70O9f2sovWOH'
    # uID = 'LTAI4GCaEY7V4Cigqxpgg1mV'
    # uKEY = 'iR3WppxVLSd5BPx58WeAy5PA0r5g0h'
    # text = '我爱你，爱你爱爱爱爱哎哎哎'
    # voice = 'dahu'  # 发音人

    token = get_token(uID, uKEY)
    # 采用RFC 3986规范进行urlencode编码。
    textUrlencode = text
    # Python 2.x请使用urllib.quote。
    # textUrlencode = urllib.quote(textUrlencode, '')
    # Python 3.x请使用urllib.parse.quote_plus。
    textUrlencode = urllib.parse.quote_plus(textUrlencode)
    textUrlencode = textUrlencode.replace("+", "%20")
    textUrlencode = textUrlencode.replace("*", "%2A")
    textUrlencode = textUrlencode.replace("%7E", "~")
    print('text: ' + textUrlencode)
    audioSaveFile = saveName   #good.mp3  文件名
    format = 'mp3'
    sampleRate = 16000
    # GET请求方式
    processGETRequest(appKey, token, textUrlencode, audioSaveFile, format, sampleRate, voice,volume)
if __name__ == '__main__':
    appKey = 'Afmo70O9f2sovWOH'
    uID = 'LTAI4GCaEY7V4Cigqxpgg1mV'
    uKEY = 'iR3WppxVLSd5BPx58WeAy5PA0r5g0h'
    text = 'etc全称Electronicetc全称ElectronicTollTollCollection，意思是全自动电子收费系统，是国际上正在努力开发并推广的一种用于公路、大桥和隧道的电子自动收费系统，是智能交通系统的服务功能之一Collection，意思是全自动电子收费系统，是国际上正在努力开发并推广的一种用于公路、大桥和隧道的电子自动收费系统，是智能交通系统的服务功能之一'
    voice = 'dahu'  # 发音人
    saveName = 'good.mp3'
    volume = 100
    makeMp3(appKey,uID,uKEY,text,voice,saveName,volume)

