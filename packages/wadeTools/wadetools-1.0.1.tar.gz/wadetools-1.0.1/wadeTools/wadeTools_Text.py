# encoding=utf-8
'''关于文字/文本处理的专用库'''
# 取出两个字符串中间的部分,用在查找匹配上贼好用

import re
import re
# 替换非法字符
def sanitize_folder_name(title):
    # 替换非法字符为下划线
    sanitized = re.sub(r'[\\/?:*"<>|]', '_', title)
    # 可选：去除首尾空格
    sanitized = sanitized.strip()
    return sanitized


def getDefaultBadWords():  #垃圾词，返回列表
    badWordList = ["此用户未填写评",
                   "此用户未及时填写评价",
                   "差",
                   "坏",
                   "黑心",
                   "不好",
                   "此用户没有填写评价",
                   "太垃圾",
                   "辣鸡",
                   "太差",
                   "恶心",
                   "骂",
                   "太慢",
                   "差评",
                   "破了",
                   "烂",
                   "垃圾",
                   "质量差",
                   "不要买",
                   "差评",
                   "坏了",
                   "刷",
                   "评论",
                   "别买",
                   "后悔",
                   "真烂",
                   "寒心",
                   "辣鸡",
                   "不推荐",
                   "太差",
                   "慎重买",
                   "投诉",
                   "退货",
                   "不负责任",
                   "有缺陷",
                   "傻逼",
                   "fuck",
                   "滚你",
                   "坑爹",
                   "**",
                   ]
    return badWordList


def wade_match_MiddleText(A, B, content):
    regex1 = re.compile(rf'{A}(.*?){B}')
    print(regex1)
    reResult = regex1.findall(content)
    print(reResult)
    return reResult


def delBadItemFromList(dataList: list, badWordList: list):  # 把字符串列表中，不想要的条目删去
    for badWord in badWordList:
        for item in dataList[::-1]:
            if badWord in item:
                dataList.remove(item)


    return [filter_str(i) for i in dataList]  # 在filter_str过滤下非法字符

# 过滤任何垃圾字符
def filter_str(desstr, restr=''):
    # 过滤除中英文及数字以外的其他字符
    res = re.compile("[^\\u4e00-\\u9fa5^a-z^A-Z^0-9^:^：^！^@^#^￥^%^&^（^）^(^)^$^!^@^^_^+]")
    return res.sub(restr, desstr)

if __name__ == '__main__':
    datalist = ["我爱你", "我杀了你"]
    badWordList = ['了']
    print(delBadItemFromList(datalist, badWordList))
    print(filter_str("我爱你:!@"))
