def baiduORC_API(path):
    # python百度ai的身份证识别代码
    # pip install baidu-aip
    from aip import AipOcr
    # 定义常量
    APP_ID = '10736496'  # 你百度帐号上的APP_ID
    API_KEY = 'xLwFVx76ZmGujNxFGSGp8wUc'  # 你百度帐号上的API_KEY
    SECRET_KEY = 'H6jpVPX3wRdcxKf59r0qoGvG6zfHnMEk'  # 你百度帐号上的SECRET_KEY

    # 初始化AipFace对象
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    """ 读取图片 """

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    image = get_file_content(path)  # 将左侧括号内1.jpg替换为待识别的图片路径

    try:
        # print(type(image))
        """ 调用身份证识别 """
        result = client.basicGeneral(image)
        print(result)

        # if result["words_result"]["公民身份号码"]["words"] =="":
        #     return None
        # else:
        #     # print("姓名：", result["words_result"]["姓名"]["words"])
        #     # print("性别：", result["words_result"]["性别"]["words"])
        #     # print("民族：", result["words_result"]["民族"]["words"])
        #     # print("生日：", result["words_result"]["出生"]["words"])
        #     # print("身份证号：", result["words_result"]["公民身份号码"]["words"])
        #     # print("住址：", result["words_result"]["住址"]["words"])
        #     return result
    except Exception as e:
        print(e)

baiduORC_API('fenlei2.png')

'''
1.国际
2.体育
3.娱乐
4.社会
5.财经
6.互联网
7.科技
8.房产
9.汽车
10.教育
11.时尚
12.游戏
13.军事
14.旅游
15.生活
16.创意
17.搞笑
18.美图
19.女人
20.美食
21.家居
22.健康
23.两性
24.情感
25.育儿
26.文化
27.历史
28.宠物
29.科学
30.动漫
31.职场
32.三农
33.悦读
34.辟谣



'''