#coding:utf-8
import copy
import hashlib
import json
import operator
import random

import requests
from wadeTools import wadeTools_Request,wadeTools_UserJSON
'''大淘客加密请求详情'''
def get_dtk_detail(skuIds,appKey,appSecret,version):  #通过商品id获取商品信息
    url = 'https://openapi.dataoke.com/api/dels/jd/goods/get-details'
    def md5_sign(args=None):
        def md5(arg):
            md5 = hashlib.md5()
            loc_bytes_utf8 = arg.encode(encoding="utf-8")
            md5.update(loc_bytes_utf8)
            return md5.hexdigest()

        copy_args = args
        # 对传入的参数 按照key 排序
        sorted_args = sorted(copy_args.items(), key=operator.itemgetter(0))
        tmp = []
        for i in sorted_args:
            tmp.append('{}={}'.format(list(i)[0], list(i)[1]))
        sign = md5('&'.join(tmp) + '&' + 'key={}'.format(appSecret)).upper()
        copy_args['sign'] = sign
        return copy_args
    sign = md5_sign({'appKey': appKey, 'version': version, 'skuIds': skuIds})
    wadeTools_Request.wade_Request_get_byParams(url,addHeader={},params=sign)
    html = requests.get(url, params=sign)

    return html

def getMyLink(materialId,appKey,appSecret,version,unionId,limitLength):
    # 京东转链
    url = 'https://openapi.dataoke.com/api/dels/jd/kit/promotion-union-convert'
    def md5_sign(args=None):
        def md5(arg):
            md5 = hashlib.md5()
            loc_bytes_utf8 = arg.encode(encoding="utf-8")
            md5.update(loc_bytes_utf8)
            return md5.hexdigest()

        copy_args = args
        # 对传入的参数 按照key 排序
        sorted_args = sorted(copy_args.items(), key=operator.itemgetter(0))
        tmp = []
        for i in sorted_args:
            tmp.append('{}={}'.format(list(i)[0], list(i)[1]))
        sign = md5('&'.join(tmp) + '&' + 'key={}'.format(appSecret)).upper()
        copy_args['sign'] = sign
        return copy_args
    sign = md5_sign({'materialId': materialId,'appKey': appKey, 'version': version, 'unionId': unionId,'chainType': 3})
    response = wadeTools_Request.wade_Request_get_byParams(url,addHeader={},params=sign)
    print(response.json())
    longURL = response.json()['data']['longUrl']
    if len(longURL)>=200:
        return response.json()['data']['shortUrl']
    else:
        return longURL


# 百度下拉长尾词
def baiduXiaLaWords(word):
    try:
        response = requests.get(url=f'http://suggestion.baidu.com/su?wd=word')
        baiduWordsList = json.loads(response.text.lstrip('window.baidu.sug(').rstrip(""");""").lstrip('{q:"冰箱",p:false,').rstrip('}'))
        random.shuffle(baiduWordsList)
        return baiduWordsList
    except:
        return []
if __name__ == '__main__':

    baiduXiaLaWords('长尾词')
    baiduLongWords =baiduXiaLaWords(word="fdsaf").__iter__()
    exit()
    appKey = '624d402f66ea7'
    appSecret = '91e0ac86eaf158f2027c740927f27fdb'
    version = 'v1.0.1'  # 当前版本号
    skuIds = 10037813209308  #京东的商品内容
    materialId = f'https://item.jd.com/{skuIds}.html'
    unionId = "1001706833" #推广者
    # limitLength = 200 # 推广链接的长度
    item_detailJson = get_dtk_detail(skuIds,appKey,appSecret,version).json()
    # print(item_detailJson)  # 打印商品详情
    from wadeTools import wadeTools_UserJSON
    actualPrice= wadeTools_UserJSON.get_dict_by_key(will_find_dist=item_detailJson,find_keys='actualPrice')
    detailImages= wadeTools_UserJSON.get_dict_by_key(will_find_dist=item_detailJson,find_keys='detailImages')[0]
    print(actualPrice,detailImages)
    # exit()
    print(getMyLink(materialId,appKey,appSecret,version,unionId,200))
    # jd_skuName = wadeTools_UserJSON.get_dict_by_key(get_dtk_detail(skuIds,appKey,appSecret,version).json(), find_keys='skuName')  # 商品名
    # jd_originPrice = wadeTools_UserJSON.get_dict_by_key(get_dtk_detail(skuIds,appKey,appSecret,version).json(), find_keys='originPrice')  # 原价
    # jd_commission = wadeTools_UserJSON.get_dict_by_key(get_dtk_detail(skuIds,appKey,appSecret,version).json(), find_keys='commission')  # 佣金
    # print(jd_skuName,jd_originPrice,jd_commission)


