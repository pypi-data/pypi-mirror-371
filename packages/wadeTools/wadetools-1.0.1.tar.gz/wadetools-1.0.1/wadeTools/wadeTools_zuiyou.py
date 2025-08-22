#!/usr/bin/env python
# coding=utf-8
# 最右 加词api
import time

import requests
import json

from wadeTools.wadeTools_Print import wadePrint



def easy回填(project_id):
    # 一次性回填，只需要填写工程名就行
    import requests
    import json

    url = "https://newapi.thed1g.com/v2api/keyword/myKeywordList"

    payload = json.dumps({
        "project_id": f"{project_id}",
        "type": 0,
        "status": -1,
        "page": 1,
        "list_rows": 500,
        "keyword": ""
    })
    headers = {
        'Host': 'newapi.thed1g.com',
        'content-type': 'application/json',
        'xweb_xhr': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309080f)XWEB/8461',
        'token': '6b62389f691d4d8b1b9d0279b2f47135',
        'schoolo': 'd01cdb015332f142e0e6e510e8855f89',
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wxbe60c88472c90f82/123/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    print(json.loads(response.text)['data']['data'])
    dataList = json.loads(response.text)['data']['data']
    for item in dataList:
        if item['status_text']=='待发布': # 审核通过的词
            # 提交回填
            item_id = item['id']
            project_id = item['project_id']
            title = item['keyword']
            create_time = item['create_time']
            article_url = item['create_time']
            回填(project_id=project_id,title=title,create_time=create_time,item_id=item_id)
            time.sleep(4)
        else:
            print(f"{item['keyword']}   ，{item['status_text']}")

def 回填(project_id,title,create_time,item_id):
    import requests
    import json
    from datetime import datetime

    # 获取当前日期和时间
    now = datetime.now()

    # 格式化日期为 "YYYY-MM-DD"
    formatted_date = now.strftime("%Y-%m-%d")

    # print(formatted_date)
    url = "https://newapi.thed1g.com/api/keyword/publish"

    payload = json.dumps({
        "keywordInfo": {
            "title": title,
            "create_time": create_time,
            "id": item_id,
            "project_id": project_id
        },
        "is_add": 0,
        "formData": [
            {
                "video_url": "https://v.douyin.com/iR7toCUa/",
                "play_num": "",
                "like_num": "",
                "publish_platform": "抖音KOC",
                "account_name": "张博绝绝子",
                "account_id": 510957,
                "publish_time": f"{formatted_date}"
            }
        ]
    })
    headers = {
        'Host': 'newapi.thed1g.com',
        'content-type': 'application/json',
        'xweb_xhr': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309080f)XWEB/8461',
        'token': '6b62389f691d4d8b1b9d0279b2f47135',
        'schoolo': 'd01cdb015332f142e0e6e510e8855f89',
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wxbe60c88472c90f82/123/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    wadePrint(response.text)


def addMyWord_ZUIYOU(addword,wenzhangurl,project_id):
    print(addword,wenzhangurl,project_id)

    import requests
    import json

    url = "https://newapi.thed1g.com/v2api/KeywordV5/add"

    payload = json.dumps({
        "formData": [
            [
                {
                    "front_msg": "5-20个汉字",
                    "max_len": 20,
                    "min_len": 5,
                    "name": f"addword",
                    "field": "keyword",
                    "var_type": 2,
                    "is_empty": 1,
                    "is_copy": 1,
                    "type": 0,
                    "value":addword,
                    "typeList": [
                        ""
                    ]
                },
                {
                    "front_msg": "",
                    "max_len": 0,
                    "min_len": 0,
                    "name": "文章链接",
                    "field": "article_url",
                    "var_type": 1,
                    "is_empty": 1,
                    "is_copy": 1,
                    "type": 0,
                    "value": f"{wenzhangurl}",
                    "typeList": [
                        ""
                    ]
                }
            ]
        ],
        "project_id": f"{project_id}"
    })
    headers = {
        'Host': 'newapi.thed1g.com',
        'content-type': 'application/json',
        'xweb_xhr': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309001c)XWEB/8461',
        'token': '6b62389f691d4d8b1b9d0279b2f47135',
        'schoolo': 'd01cdb015332f142e0e6e510e8855f89',
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wxbe60c88472c90f82/119/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


if __name__ == '__main__':




    # addword = '女指导员的哀嚎'
    # wenzhangurl = 'http://dy.163.com/v2/article/detail/II9TMH1A052188CT.html'
    # addMyWord_ZUIYOU(addword,wenzhangurl,52)
    easy回填(project_id=52)
    # 回填(project_id=52, title="晴晴资金录", create_time="2023-11-30 16:36:39", item_id=5159)
