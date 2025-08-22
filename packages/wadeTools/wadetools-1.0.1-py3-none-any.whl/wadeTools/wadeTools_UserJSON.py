import json
import time
'''
这里是关于json内容的工具库
#再也不用一个一个找JSON的位置了，直接查找，返回第一项匹配的字符串，如果找不到反馈"空值"
get_dict_by_key(will_find_dist, find_keys):  # will_find_dist要查找的字典，find_keys要查找的keys，found找到值存放处

get_dict_by_key_method(will_find_dist, find_keys)  #返回的类型是列表，空的返回[]


'''
def getValueList_From_Dict_By_Key_ExceptSbKey(will_find_dist, find_keys,notWantKeyList):  # will_find_dist要查找的字典，find_keys要查找的keys，found找到值存放处,notWantKeyList 把不需要遍历的列表放进去 ["不想要的key1","不想要的Key2"]
    value_found = []
    if (isinstance(will_find_dist, (list))):  # 含有列表的值处理
        if (len(will_find_dist) > 0):
            for now_dist in will_find_dist:
                found = get_dict_by_key_method(now_dist, find_keys)
                if (found):
                    value_found.extend(found)
            return value_found

    if (not isinstance(will_find_dist, (dict))):  # 没有字典类型的了
        return 0

    else:  # 查找下一层
        dict_key = will_find_dist.keys()
        # print (dict_key)
        for i in dict_key:
            if i in notWantKeyList:
                continue
            if (i == find_keys):
                value_found.append(will_find_dist[i])
            found = get_dict_by_key_method(will_find_dist[i], find_keys)
            if (found):
                value_found.extend(found)
        return value_found

def get_dict_by_key_method(will_find_dist, find_keys):  # will_find_dist要查找的字典，find_keys要查找的keys，found找到值存放处
    value_found = []
    if (isinstance(will_find_dist, (list))):  # 含有列表的值处理
        if (len(will_find_dist) > 0):
            for now_dist in will_find_dist:
                found = get_dict_by_key_method(now_dist, find_keys)
                if (found):
                    value_found.extend(found)
            return value_found

    if (not isinstance(will_find_dist, (dict))):  # 没有字典类型的了
        return 0

    else:  # 查找下一层
        dict_key = will_find_dist.keys()
        # print (dict_key)
        for i in dict_key:
            if (i == find_keys):
                value_found.append(will_find_dist[i])
            found = get_dict_by_key_method(will_find_dist[i], find_keys)
            if (found):
                value_found.extend(found)
        return value_found
def get_dict_by_key(will_find_dist, find_keys):  # will_find_dist要查找的字典，find_keys要查找的keys，found找到值存放处
    result = get_dict_by_key_method(will_find_dist, find_keys)
    if len(result) ==0:
        return '空值'
    else:
        return result[0]

def readjson(jsonname):
    with open(jsonname, 'r',encoding='utf-8') as f:
        data = json.load(f)

    return data

def savejson(data,jsonname):
    # Writing JSON data
    with open(jsonname, 'w',encoding='utf-8') as f:
        json.dump(data, f,ensure_ascii=False, indent=4)


def createJsonFile(jsonname):
    initJson = {}
    savejson(initJson, jsonname)

def jsonDataAdd(jsonname,userName,num):
    userjson = readjson(jsonname)
    DataTime = time.strftime('%Y%m%d', time.localtime(time.time()))
    name = userName
    numm = num
    userjson[name] = [numm, DataTime]
    savejson(userjson, jsonname)

# json清空记录初始化
def jsonDateInit(jsonname):
    userjson = readjson(jsonname)
    DataTime = time.strftime('%Y%m%d', time.localtime(time.time()))
    for user in userjson:
        userjson[user][0] = 0
        userjson[user][1] = DataTime
    savejson(userjson,jsonname)
    print('json初始化成功')

def jsonClearAllUsers(jsonname):
    userjson = readjson(jsonname)
    userjson.clear()
    savejson(userjson,jsonname)

def deletUser(username,jsonname):
    userjson = readjson(jsonname)
    if username in userjson:
        userjson.pop(username)
        savejson(userjson,jsonname)
        print(f"成功删除用户:{username}")
    else:
        print("不存在该用户")

def getUserPOSTNum(username,jsonname):
    userjson = readjson(jsonname)
    if username in userjson:
        return userjson[username][0]
    else:
        print("不存在该用户")


if __name__ == '__main__':
    jsonname ='user.json'
    deletUser('用户名',jsonname)   #删除用户
    #
    # jsonDataAdd(jsonname,'xiaohong',3) #增加用户
    #
    # jsonDateInit(jsonname)  #初始化用户次数
    # jsonClearAllUsers(jsonname)

    # getUserPOSTNum('xiaohu', jsonname)  #

    # createJsonFile(jsonname)  #初始化
