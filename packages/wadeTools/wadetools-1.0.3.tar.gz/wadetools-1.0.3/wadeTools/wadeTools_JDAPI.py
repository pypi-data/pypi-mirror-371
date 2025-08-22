#coding:utf-8
import random
import time
from threading import Thread
from DrissionPage import WebPage, ChromiumOptions
from DrissionPage.errors import ElementNotFoundError
from DrissionPage.common import Keys
import requests
import json
import re
from wadeTools import wadeTools_error, wadeTools_Police, wadeTools_path, wadeTools_feishu
from wadeTools import wadeTools_UserJSON, wadeTools_Text
from retrying import retry
from wadeTools.wadeTools_Request import HEADERS
from wadeTools.wadeTools_Print import wadePrint
# 这个类以后要扩展很多接口
class JDSpider():
    @wadeTools_Police.safe_Mode([],[],'爬评论出错')
    @retry(stop_max_attempt_number=5,wait_random_min=3)
    def spider_Newcomment(self, id, page,proxies=None,sortType=5):

        """爬最新的评论，只负责爬评论，其他的啥都不管， 输入商品ID,page，输出  commentList, imgList, '😆jdmain转换正常'  # 打乱重拍
        score 0全部评论 1是差评 2是中评 3是好评
        sortType 5是热评排序 6是时间排序 7是视频评论
        """
        url = f'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId={id}&score=3&sortType={sortType}&page={page}&pageSize=10&isShadowSku=0&rid=0&fold=1'
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': random.choice(HEADERS),
            'Connection': 'keep-alive',
            'Host': 'club.jd.com',
        }
        with requests.Session() as session:
            html = session.get(url=url, headers=headers,proxies=proxies,timeout=10)

        # 去掉多余得到json格式
        if html.status_code==200 and 'fetchJSON_comment' not in html.text:
            #空评价，返回空
            return ([],[],'html.status_code==200 and fetchJSON_comment not in html.text')

        if html.status_code==200:
            wadePrint(f'IP正常：当前正在请求第{page}页评论和图片数据')
        wadePrint(html.text)
        # 开始清洗数据
        content = html.text.strip('fetchJSON_comment98vv995();')
        content = content.strip('fetchJSON_comment98vv37();')
        json_flag = json.loads(content, strict=False)  # 收到的str内容进行清洗处理，变成可用的json，处理好了

        # wadePrint('jdmain运行成功（京东爬虫主程序）')
        JSONlist = json_flag["comments"]
        if JSONlist == []:  #空的说明本页本身无内
            return ([], [], f'第{page}页评论数据为空')
        commentList = []
        imgList = []
        # wadePrint(JSONlist)

        for item in JSONlist:

            commentList.extend(wadeTools_UserJSON.getValueList_From_Dict_By_Key_ExceptSbKey(item,"content",['replies','afterUserComment']))
            imgList.extend(wadeTools_UserJSON.getValueList_From_Dict_By_Key_ExceptSbKey(item,"imgUrl",[]))
            # wadePrint(commentList)
            # 过滤垃圾评论
        commentList = wadeTools_Text.delBadItemFromList(commentList,wadeTools_Text.getDefaultBadWords())  #
        commentList = [item for item in commentList if len(item)>=10]
        commentList = sorted(commentList,key=len,reverse=True)

        # wadePrint(imgList)
        imgListNew = []
        for this_imgUrl in imgList:
            # url统一修改函数：把里边的n0字符串替换，尺寸也替换掉 改成s720x540
            if 'img30.360buyimg.com/n0/' in this_imgUrl:
                this_imgUrl = this_imgUrl.replace("img30.360buyimg.com/n0/",
                                                  "img30.360buyimg.com/n1/")
            if 's128x96_jfs/' in this_imgUrl:
                this_imgUrl = this_imgUrl.replace("s128x96_jfs/", "s720x540_jfs/")
            if '\n' in this_imgUrl:
                this_imgUrl = this_imgUrl.replace('\n', '')
            if '\r' in this_imgUrl:
                this_imgUrl = this_imgUrl.replace('\r', '')
            # if '//' in this_imgUrl:
            #     this_imgUrl = this_imgUrl.replace("//", "")
            imgListNew.append(this_imgUrl)
            del this_imgUrl  # 销毁变量

        imgList = imgListNew
        del imgListNew

        random.shuffle(commentList)
        random.shuffle(imgList)

        del content,json_flag,JSONlist
        return (commentList, imgList, '😆jdmain转换正常')  # 打乱重拍

    @wadeTools_Police.safe_Mode([])
    @retry(stop_max_attempt_number=5, wait_random_min=3)
    def spider_itemData(self, id,proxies=None):
        
        # 检查是否有商品参数库
        wadeTools_path.checkFilePath('商品参数库')
        try:
            # 如果参数库中有就不用请求了
            itemDataList = wadeTools_UserJSON.readjson(f'商品参数库/{id}')
            wadePrint(f"{id}--成功加载库中商品参数....")
            return (itemDataList)
        except FileNotFoundError:

            # wadePrint(1)
            """爬商品信息"""
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'User-Agent': random.choice(HEADERS),
                'Connection': 'keep-alive',
                'Host': 'item.jd.com',
                'cookie': '__jdu=1734234452490698444113; shshshfpa=348768b0-2db6-6975-701b-8806212a360f-1734234453; shshshfpx=348768b0-2db6-6975-701b-8806212a360f-1734234453; _base_=YKH2KDFHMOZBLCUV7NSRBWQUJPBI7JIMU5R3EFJ5UDHJ5LCU7R2NILKK5UJ6GLA2RGYT464UKXAI4Z6HPCTN4UQM3WHVQ4ENFP57OC42IY6KIHS3K6LGGVHIT4HK4V34TCNE6YVKRXISUOMSORKLWKHP26UVH46IGQS4XX2SG4SOQWCP5WPWO6EFS7HEHMRWVKBRVHB33TFD5EX5PZYGBFPE3NNFL5EMGOMYKHKDXUXEXIYMM754UEEO27G4MQ6BOJX7RLRW37V6KA2D4ZKSH4RVPCUSKABKJZDW5EDMTTJWVDYWOMZSFS6B4DTLR7CXIKFZ5Q723KWBCTLPPIF3FVZJBY; pinId=w3NN1JXR88LgQNJQMCMYmw; unick=%E7%82%B9%E6%88%91%E4%B8%8B%E5%96%AE%E6%9B%B4%E4%BE%BF%E5%AE%9C; _tp=RnXd490p0A8w6swDdN3FcA%3D%3D; _pst=jd_DgzZpkHEQlFG; __jdv=209449046|direct|-|none|-|1740040897468; areaId=7; ipLoc-djd=7-427-3557-53893; jsavif=1; jsavif=1; user-key=9715d11d-6d18-4304-be20-2a3a9b8ecccd; 3AB9D23F7A4B3C9B=SRQK3ESS76RF76R4XHLIESTUAHA6ACY2E2SZGJYIZVGVBO6BWKOZHKPPORTB7FWL52HS432WZK4TRGAV7WWUOEETFM; PCSYCityID=CN_410000_410300_0; umc_count=1; TrackID=1zufm4ELWgBwNOlOQUKYJ6bvZ8vT0k5AXW9B1hiXGVXiQGsXjQQ6wlOno-EXz-1UznUgMyM9z5dlUSpD_1w2R5wa8TeYYdYOj2U42W1C50_h_jjhLwjaT6k3gkwJzChew; thor=A950C58AE39C76DB638A05D5BB527229C34C87388D48A57AFB18AF40FE9054FEB8ED4D708DBCE7F20E7A3C8494DAA6CB45DC72D8C4E3A6FD9B0652A2C71ACEB9CA2DBB4CBA2405900006F8DE3344FBD387BF70CA8C948435B17593F6837D17FE6211659D0A98BF4326F12DBACD9055A610C2BC5E633EBEE74CB16D9EE575B81578D10704F453B63AB86A8D1DEFF152799F937B84924881A60772C47800B72EFE; light_key=AASBKE7rOxgWQziEhC_QY6yaucNZPHEVXDQhBhKS-wl950m4Di2cJsVzhagTMOKGwM0RnodC; pin=jd_DgzZpkHEQlFG; ceshi3.com=203; token=435daf8ab91a1aab57cbf171345bf05f,3,966732; 3AB9D23F7A4B3CSS=jdd03SRQK3ESS76RF76R4XHLIESTUAHA6ACY2E2SZGJYIZVGVBO6BWKOZHKPPORTB7FWL52HS432WZK4TRGAV7WWUOEETFMAAAAMVE4RAM5AAAAAADXDENVX7WBZFPQX; __jda=181111935.1734234452490698444113.1734234452.1740113207.1740116789.18; __jdb=181111935.30.1734234452490698444113|18.1740116789; __jdc=181111935; shshshfpb=BApXSOpEqJPBAccag3_GHwcLS4XGa7IfVBnZiQ3xg9xJ1MupqQ4EzsnqL7Ek; flash=3_FRLDk7Sa7Bt57bROZ0PGCuxoCmudgths6jvOueRW6cR5KQ7_deDrOgQqpBW-f_MQy8NkkJVxvHqzE9-lVuV-uSIzrVhQuXkESoBYntQOqhRAxgq5ChDFam7uyS5bzQLo2uXhCdawGXUhrXK6unx9iB0JNVMqDA_K_LOYcYGxAgOjKKAQFXfO',
            }
            mainHtml = requests.get(url=f"https://item.jd.com/{id}.html", headers=headers,proxies =proxies,timeout=10)
            wadePrint(f"https://item.jd.com/{id}.html")
            print(mainHtml.text)
            if '商品名称' not in str(mainHtml.text):
                raise wadeTools_error.Error_continue("打开网页F12，打开商品页，找到Cookie:切换后再运行")
            pattern = re.compile(r"<li title='(.*)'>(.*)：(.*)</li>")  # 查找数字
            itemDataList = pattern.findall(mainHtml.text)
            wadeTools_UserJSON.savejson(itemDataList, f'商品参数库/{id}')
            return (itemDataList)



    @wadeTools_Police.safe_Mode([])
    @retry(stop_max_attempt_number=5, wait_random_min=3)
    def spider_itemQueston(self,id,proxies=None):
        """爬产品问答模块，随心调用"""
        # try:

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': random.choice(HEADERS),
            'Connection': 'keep-alive',
            'Host': 'question.jd.com',
            'Content-Type': 'application/json'
        }

        # 请求示例 https://question.jd.com/question/getQuestionAnswerList.action?callback=jQuery8364807&page=2&productId=100008631911
        mainHtml = requests.get(
            url=f"https://question.jd.com/question/getQuestionAnswerList.action?callback=jQuery8364807&page=2&productId={id}",
            proxies=proxies,
            headers=headers,
            timeout=10)
        try:
            questionList = json.loads(mainHtml.text[14:-2])['questionList']
        except KeyError as e:
            wadePrint("问答数据是空")
            return []

        askList = []  # 做一个渲染列表给json前段渲染
        for ask in questionList:
            askJSONG = {}
            # wadePrint(ask['content'])  这个是问题
            askJSONG["QUESTION"] = ask['content']
            KEYSList = []
            for keys in ask['answerList']:
                # wadePrint(keys['content'])  这个是两个回答
                KEYSList.append(keys['content'])
            askJSONG['KEYS'] = KEYSList
            askList.append(askJSONG)

        """[{'QUESTION': '亲们收到的暖风机噪音大吗？有没有60分贝？', 'KEYS': ['刚开始声音小，后来越来越吵了', '噪音很小']}, {'QUESTION': '这个晚上用声音大吗？', 'KEYS': ['不大，挺好的', '声音是有点的，但能接受范围']}, {'QUESTION': '请问制热后有没有难闻的塑料味？？？', 'KEYS': ['没有', '没有']}, {'QUESTION': '风量大吗', 'KEYS': ['风不大，吹个一米多吧', '近距离很好']}, {'QUESTION': '可以遥控开关吗', 'KEYS': ['不可以。可以定时', '有2种款式选择   带遥控的贵点']}, {'QUESTION': '杂音和声音大不？买过的小伙伴们', 'KEYS': ['没啥杂音，不适合房间大的', '不会，加热特别快，好用']}, {'QUESTION': '我买的这款有没有遥控器？', 'KEYS': ['没有', '没有']}, {'QUESTION': '有声音吗？', 'KEYS': ['声音比较小，接受范围内，不影响', '还挺安静的']}, {'QUESTION': '请问防水吗', 'KEYS': ['没试过，尽量避免水吧。', 'IPX0防水等级，比较差，但放在浴室有点水汽问题不大，不要把谁溅到上面']}, {'QUESTION': '有小宝宝安全吗？', 'KEYS': ['相当安全', '就是买来给小宝宝换尿不湿用的']}]"""
            # wadePrint(askList)
        return (askList)

    def spider_itemByLeiMu(self,leimu = "",page= 1):
        url = "https://union.jd.com/api/goods/search"
        leimuITER = leimu.split(",").__iter__()
        # wadePrint(next(leimuITER,"null"))
        # exit()
        payload = "{\"pageNo\":"+str(page)+",\"pageSize\":60,\"searchUUID\":\"7b3dac2a9cc74fc8b3349161f203f4a6\",\"data\":{\"bonusIds\":null,\"categoryId\":"+next(leimuITER,"null")+",\"cat2Id\":"+next(leimuITER,"null")+",\"cat3Id\":"+next(leimuITER,"null")+",\"deliveryType\":0,\"fromCommissionRatio\":null,\"toCommissionRatio\":null,\"fromPrice\":null,\"toPrice\":null,\"hasCoupon\":0,\"isHot\":null,\"preSale\":0,\"isPinGou\":0,\"jxFlag\":0,\"isZY\":0,\"isCare\":0,\"lock\":0,\"orientationFlag\":0,\"sort\":\"desc\",\"sortName\":\"inOrderCount30Days\",\"searchType\":\"st3\",\"keywordType\":\"kt0\"}}"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://union.jd.com',
            # 'Cookie': 'ssid="CuFN9wVpT7Co5gL20lq3Ow=="'
        }
        wadePrint(payload)
        response = requests.request("POST", url, headers=headers, data=payload)

        resultList = wadeTools_UserJSON.get_dict_by_key_method(response.json(),'skuId')
        return resultList
    def spider_itemBaiduSearch(self,keyword,page= 1):
        """
            获取百度搜索下拉词推荐列表
            :param keyword: 搜索关键词
            :return: 下拉词推荐列表
            """
        url = "https://suggestion.baidu.com/su"
        params = {
            "wd": keyword,  # 搜索关键词
            "cb": "jQuery11020231084039737774_1678901234567",  # 回调函数名，可随意填写
            "_": "1678901234567"  # 时间戳，可随意填写
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            # 去除JSONP的回调函数包装
            json_str = response.text.strip().replace(params["cb"] + "(", "").rstrip(");")
            import json
            data = json.loads(json_str)
            suggestions = data.get("s", [])
            return suggestions
        except requests.RequestException as e:
            print(f"请求出错: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON解析出错: {e}")
        return []
class JDSpider_Drissionpage():
    """
    因为接口失效，采用模拟浏览器的方法取内容
    """
    def spider_Newcomment(self, id):
        co = ChromiumOptions(read_file=False).set_paths(local_port='9888',
                                                        browser_path=r'.\chrome\Chrome.exe',
                                                        user_data_path=r'.\Chrome\userData')
        # co.headless(True)  # 无头模式
        # co.set_argument('--no-headless')
        # co.set_argument('--no-sandbox')  # 无沙盒模式
        # co.set_argument('--headless=new')  # 无界面系统添加
        co.set_argument('--start-maximized')
        # 创建 WebPage 实例并传入 chromium_options
        page = WebPage(chromium_options=co, session_or_options=False)
        # page.set.window.normal()
        # page.set.window.hide()
        page.set.window.show()
        # 调用已有的最大化方法将窗口最大化
        page.set.window.max()
        # page.set.window.max()
        # page.set.window.mini()


        # 注意：session_or_options=False
        page.get(f"https://item.jd.com/{id}.html")
        page.wait.new_tab(timeout=2)
        tab = page.latest_tab
        wadePrint(tab.title)
        wadePrint(page.html)
        api_prefix = "https://api.m.jd.com/client.action"
        page.listen.start(targets=api_prefix, method="POST")  # 监听包含指定前缀的URL
        print("监听器已启动，开始访问页面...")
        page.ele('@@tag()=div@@text()=全部评价').click()
        time.sleep(2)


        packet = page.listen.wait(timeout=10)  # 获取1个符合条件的数据包

        if not packet:
            print("超时未获取到目标API数据包")
            return None

        # 6. 解析数据包内容
        print(f"成功捕获API: {packet.url}")
        # 响应体自动解析为JSON（若为JSON格式）

        api_data = packet.response.body #抓到的是dict格式
        print(api_data)
        wadePrint(type(api_data))

        content = api_data
        # from wadeTools import wadeTools_txt
        # TXT111 = wadeTools_txt.wadeTxtObject(filename='111.txt')
        # TXT111.additem_to_Txt(page.html)
        if page.latest_tab.title == "京东-欢迎登录-登陆后按回车继续":
            # 遇到京东验证了
            wadeTools_feishu.send_feishu_message(fr"❎❎❎❎京东-欢迎登录")

            input("京东-欢迎登录-登陆后按回车继续")  # 程序会在这里暂停，直到用户按下回车键
        if page.latest_tab.title == "京东验证":
            # 遇到京东验证了
            wadeTools_feishu.send_feishu_message(fr"❎❎❎❎京东-验证")

            input("验证后--按回车继续")  # 程序会在这里暂停，直到用户按下回车键



        #判断评论的个数

        commentList = wadeTools_UserJSON.get_dict_by_key_method(content, "commentData")
        imgList = wadeTools_UserJSON.get_dict_by_key_method(content, "largePicURL")

        commentList = wadeTools_Text.delBadItemFromList(commentList, wadeTools_Text.getDefaultBadWords())  #
        commentList = [item for item in commentList if len(item) >= 6]
        commentList = sorted(commentList, key=len, reverse=True)

        # wadePrint(imgList)
        imgListNew = []
        for this_imgUrl in imgList:
            # url统一修改函数：把里边的n0字符串替换，尺寸也替换掉 改成s720x540
            if 'img30.360buyimg.com/n0/' in this_imgUrl:
                this_imgUrl = this_imgUrl.replace("img30.360buyimg.com/n0/",
                                                  "img30.360buyimg.com/n1/")
            if 's128x96_jfs/' in this_imgUrl:
                this_imgUrl = this_imgUrl.replace("s128x96_jfs/", "s720x540_jfs/")
            if '\n' in this_imgUrl:
                this_imgUrl = this_imgUrl.replace('\n', '')
            if '\r' in this_imgUrl:
                this_imgUrl = this_imgUrl.replace('\r', '')
            # if '//' in this_imgUrl:
            #     this_imgUrl = this_imgUrl.replace("//", "")
            imgListNew.append(this_imgUrl)
            del this_imgUrl  # 销毁变量

        imgList = imgListNew
        del imgListNew

        random.shuffle(commentList)
        random.shuffle(imgList)

        del content
        return (commentList, imgList, '😆jdmain转换正常')  # 打乱重拍

        # return (commentList, imgList, '😆jdmain转换正常')  # 打乱重拍

    @wadeTools_Police.safe_Mode([])
    # @retry(stop_max_attempt_number=5, wait_random_min=3)
    def spider_itemData(self, id,proxies=None):

        # 检查是否有商品参数库
        wadeTools_path.checkFilePath('商品参数库')
        try:
            # 如果参数库中有就不用请求了
            itemDataList = wadeTools_UserJSON.readjson(f'商品参数库/{id}')
            wadePrint(f"{id}--成功加载库中商品参数....")
            return (itemDataList)
        except FileNotFoundError:

            # wadePrint(1)
            """爬商品信息"""

            co = ChromiumOptions(read_file=False).set_paths(local_port='9888',
                                                            browser_path=r'.\chrome\Chrome.exe',
                                                            user_data_path=r'.\Chrome\userData')
            # co.headless(True)  # 无头模式
            # co.set_argument('--no-headless')
            # co.set_argument('--no-sandbox')  # 无沙盒模式
            # co.set_argument('--headless=new')  # 无界面系统添加
            co.set_argument('--start-maximized')
            # 创建 WebPage 实例并传入 chromium_options
            page = WebPage(chromium_options=co, session_or_options=False)
            # page.set.window.normal()
            # page.set.window.hide()
            page.set.window.show()
            # 调用已有的最大化方法将窗口最大化
            page.set.window.max()
            # page.set.window.max()
            # page.set.window.mini()

            # page.listen.start(targets=api_prefix)  # 监听包含指定前缀的URL
            print("监听器已启动，开始访问页面...")
            # 注意：session_or_options=False
            page.get(f"https://item.jd.com/{id}.html")
            page.wait.new_tab(timeout=2)
            tab = page.latest_tab
            wadePrint(tab.title)
            wadePrint(page.html)
            # from wadeTools import wadeTools_txt
            # TXT111 = wadeTools_txt.wadeTxtObject(filename='111.txt')
            # TXT111.additem_to_Txt(page.html)
            if page.latest_tab.title == "京东-欢迎登录":
                # 遇到京东验证了
                input("京东-欢迎登录-登陆后按回车继续")  # 程序会在这里暂停，直到用户按下回车键
            if page.latest_tab.title == "京东验证":
                # 遇到京东验证了
                input("验证后--按回车继续")  # 程序会在这里暂停，直到用户按下回车键

            def parse_goods_html_with_re(html):
                """
                使用正则表达式解析商品属性HTML，提取名称和内容生成itemDataList

                参数:
                    html: 包含商品属性的HTML字符串
                返回:
                    itemDataList: 列表，每个元素为[序号, 名称, 内容]
                """
                # 正则表达式模式：匹配每个item块中的name和text内容
                # 先匹配整个item块，再从中提取name和text
                item_pattern = re.compile(
                    r'<div class="item[^>]*?>.*?'  # 匹配item开始标签
                    r'<div class="name">(.*?)</div>.*?'  # 提取name内容
                    r'<div class="text">(.*?)</div>.*?'  # 提取text内容
                    r'</div>',  # 匹配item结束标签
                    re.DOTALL  # DOTALL模式让.匹配包括换行符在内的所有字符
                )

                # 查找所有匹配的item
                matches = item_pattern.findall(html)

                itemDataList = []
                for index, (name, content) in enumerate(matches, 1):
                    # 清理名称和内容中的多余空白、HTML标签
                    clean_name = re.sub(r'<.*?>', '', name).strip()  # 移除可能的嵌套标签
                    clean_content = re.sub(r'<.*?>', '', content).strip()  # 移除a标签等

                    itemDataList.append([index, clean_name, clean_content])

                return itemDataList

            # 解析并打印结果
            itemDataList = parse_goods_html_with_re(page.html)
            print("生成的itemDataList:")
            for item in itemDataList:
                print(item)

            # 演示使用方式
            # print("\n使用示例:")
            # for items in itemDataList:
            #     itemName = items[1]
            #     itemContent = items[2]
            #     print(f"{itemName}: {itemContent}")
            wadeTools_UserJSON.savejson(itemDataList, f'商品参数库/{id}')
            return (itemDataList)



    @wadeTools_Police.safe_Mode([])
    @retry(stop_max_attempt_number=5, wait_random_min=3)
    def spider_itemQueston(self,id,proxies=None):
        """爬产品问答模块，随心调用"""
        # try:

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': random.choice(HEADERS),
            'Connection': 'keep-alive',
            'Host': 'question.jd.com',
            'Content-Type': 'application/json'
        }

        # 请求示例 https://question.jd.com/question/getQuestionAnswerList.action?callback=jQuery8364807&page=2&productId=100008631911
        mainHtml = requests.get(
            url=f"https://question.jd.com/question/getQuestionAnswerList.action?callback=jQuery8364807&page=2&productId={id}",
            proxies=proxies,
            headers=headers,
            timeout=10)
        try:
            questionList = json.loads(mainHtml.text[14:-2])['questionList']
        except KeyError as e:
            wadePrint("问答数据是空")
            return []

        askList = []  # 做一个渲染列表给json前段渲染
        for ask in questionList:
            askJSONG = {}
            # wadePrint(ask['content'])  这个是问题
            askJSONG["QUESTION"] = ask['content']
            KEYSList = []
            for keys in ask['answerList']:
                # wadePrint(keys['content'])  这个是两个回答
                KEYSList.append(keys['content'])
            askJSONG['KEYS'] = KEYSList
            askList.append(askJSONG)

        """[{'QUESTION': '亲们收到的暖风机噪音大吗？有没有60分贝？', 'KEYS': ['刚开始声音小，后来越来越吵了', '噪音很小']}, {'QUESTION': '这个晚上用声音大吗？', 'KEYS': ['不大，挺好的', '声音是有点的，但能接受范围']}, {'QUESTION': '请问制热后有没有难闻的塑料味？？？', 'KEYS': ['没有', '没有']}, {'QUESTION': '风量大吗', 'KEYS': ['风不大，吹个一米多吧', '近距离很好']}, {'QUESTION': '可以遥控开关吗', 'KEYS': ['不可以。可以定时', '有2种款式选择   带遥控的贵点']}, {'QUESTION': '杂音和声音大不？买过的小伙伴们', 'KEYS': ['没啥杂音，不适合房间大的', '不会，加热特别快，好用']}, {'QUESTION': '我买的这款有没有遥控器？', 'KEYS': ['没有', '没有']}, {'QUESTION': '有声音吗？', 'KEYS': ['声音比较小，接受范围内，不影响', '还挺安静的']}, {'QUESTION': '请问防水吗', 'KEYS': ['没试过，尽量避免水吧。', 'IPX0防水等级，比较差，但放在浴室有点水汽问题不大，不要把谁溅到上面']}, {'QUESTION': '有小宝宝安全吗？', 'KEYS': ['相当安全', '就是买来给小宝宝换尿不湿用的']}]"""
            # wadePrint(askList)
        return (askList)

    def spider_itemByLeiMu(self,leimu = "",page= 1):
        url = "https://union.jd.com/api/goods/search"
        leimuITER = leimu.split(",").__iter__()
        # wadePrint(next(leimuITER,"null"))
        # exit()
        payload = "{\"pageNo\":"+str(page)+",\"pageSize\":60,\"searchUUID\":\"7b3dac2a9cc74fc8b3349161f203f4a6\",\"data\":{\"bonusIds\":null,\"categoryId\":"+next(leimuITER,"null")+",\"cat2Id\":"+next(leimuITER,"null")+",\"cat3Id\":"+next(leimuITER,"null")+",\"deliveryType\":0,\"fromCommissionRatio\":null,\"toCommissionRatio\":null,\"fromPrice\":null,\"toPrice\":null,\"hasCoupon\":0,\"isHot\":null,\"preSale\":0,\"isPinGou\":0,\"jxFlag\":0,\"isZY\":0,\"isCare\":0,\"lock\":0,\"orientationFlag\":0,\"sort\":\"desc\",\"sortName\":\"inOrderCount30Days\",\"searchType\":\"st3\",\"keywordType\":\"kt0\"}}"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://union.jd.com',
            # 'Cookie': 'ssid="CuFN9wVpT7Co5gL20lq3Ow=="'
        }
        wadePrint(payload)
        response = requests.request("POST", url, headers=headers, data=payload)

        resultList = wadeTools_UserJSON.get_dict_by_key_method(response.json(),'skuId')
        return resultList
    def spider_itemBaiduSearch(self,keyword,page= 1):
        """
            获取百度搜索下拉词推荐列表
            :param keyword: 搜索关键词
            :return: 下拉词推荐列表
            """
        url = "https://suggestion.baidu.com/su"
        params = {
            "wd": keyword,  # 搜索关键词
            "cb": "jQuery11020231084039737774_1678901234567",  # 回调函数名，可随意填写
            "_": "1678901234567"  # 时间戳，可随意填写
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            # 去除JSONP的回调函数包装
            json_str = response.text.strip().replace(params["cb"] + "(", "").rstrip(");")
            import json
            data = json.loads(json_str)
            suggestions = data.get("s", [])
            return suggestions
        except requests.RequestException as e:
            print(f"请求出错: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON解析出错: {e}")
        return []



# 这个类以后要扩展很多接口
class TBSpider():
    def spider_comment(self, id, page):
        """爬评论"""
        # try:
        HEADERS = [
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.95 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
            'Mozilla/5.0 (Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
        ]
        # url = f'https://club.jd.com/productpage/p-{id}-s-3-t-5-p-0.html?callback=fetchJSON_comment98vv37'

        url = f'https://rate.tmall.com/list_detail_rate.htm?itemId=524673596684&spuId=473544268&sellerId=2594916711&order=3&currentPage=4&pageSize=20&append=0&picture=0'
        # else:
        #     url = f'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId={id}&score=3&sortType=6&page={page}0&pageSize=10&isShadowSku=0&fold=1'
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': random.choice(HEADERS),
            'Connection': 'keep-alive',
            # 'Host': 'club.jd.com',
        }
        # wadePrint(url)
        html = requests.get(url=url, headers=headers)
        # wadePrint(html.text)
        # # 去掉多余得到json格式
        # content = html.text.strip('fetchJSON_comment98vv995();')
        # content = content.strip('fetchJSON_comment98vv37();')
        # json_flag = json.loads(content, strict=False)  # 收到的str内容进行清洗处理，变成可用的json，处理好了
        #
        # wadePrint('jdmain运行成功（京东爬虫主程序）')
        # JSONlist = json_flag["comments"]
        # if JSONlist == []:
        #     wadePrint('JDSpider评论为空')
        #     return [], [], '😅JDSpider爬虫评论为空'
        # commentList = []
        # imgList = []
        #
        # for num in range(0, len(JSONlist) - 1):
        #     if 'content' in JSONlist[num] and len(commentList) < 150000:  # 若存在内容，并且内容条数少于4条
        #         if len(JSONlist[num]['content']) <= 300 and len(JSONlist[num]['content']) >= 8:  # 控制字符150以内
        #             if '此用户未填写评' in JSONlist[num]['content'] \
        #                     or '垃圾' in JSONlist[num]['content'] \
        #                     or '不要买' in JSONlist[num]['content'] \
        #                     or '差评' in JSONlist[num]['content'] \
        #                     or '坏了' in JSONlist[num]['content'] \
        #                     or '刷' in JSONlist[num]['content'] \
        #                     or '评论' in JSONlist[num]['content'] \
        #                     or '别买' in JSONlist[num]['content'] \
        #                     or '后悔' in JSONlist[num]['content'] \
        #                     or '真烂' in JSONlist[num]['content'] \
        #                     or '寒心' in JSONlist[num]['content'] \
        #                     or '辣鸡' in JSONlist[num]['content'] \
        #                     or '差' in JSONlist[num]['content'] \
        #                     or '差' in JSONlist[num]['content'] \
        #                     or '慎重买' in JSONlist[num]['content'] \
        #                     or '投诉' in JSONlist[num]['content'] \
        #                     or '退货' in JSONlist[num]['content'] \
        #                     or '有缺陷' in JSONlist[num]['content'] \
        #                     or '不负责任' in JSONlist[num]['content'] \
        #                     or '**' in JSONlist[num]['content'] \
        #                     :
        #                 wadePrint('忽略内容--------------------------------------------')
        #                 pass
        #             else:
        #                 commentList.append(JSONlist[num]['content'].replace('\n', '').replace('\r', ''))
        #         else:
        #             continue
        # for num in range(0, len(JSONlist) - 1):
        #     if 'images' in JSONlist[num] and len(imgList) < 10000:  # 若存在内容，并且内容条数少于4条
        #         for imgNum in range(0, len(JSONlist[num]['images'])):
        #             if 'imgUrl' in JSONlist[num]['images'][imgNum]:  # 控制字符150以内
        #                 this_imgUrl = JSONlist[num]['images'][imgNum]['imgUrl']
        #                 # url统一修改函数：把里边的n0字符串替换，尺寸也替换掉 改成s720x540
        #                 if 'img30.360buyimg.com/n0/' in this_imgUrl:
        #                     this_imgUrl = this_imgUrl.replace("img30.360buyimg.com/n0/",
        #                                                       "img30.360buyimg.com/n1/")
        #                 if 's128x96_jfs/' in this_imgUrl:
        #                     this_imgUrl = this_imgUrl.replace("s128x96_jfs/", "s720x540_jfs/")
        #                 if '\n' in this_imgUrl:
        #                     this_imgUrl = this_imgUrl.replace('\n', '')
        #                 if '\r' in this_imgUrl:
        #                     this_imgUrl = this_imgUrl.replace('\r', '')
        #                 # if '//' in this_imgUrl:
        #                 #     this_imgUrl = this_imgUrl.replace("//", "")
        #                 imgList.append(this_imgUrl)
        #                 del this_imgUrl  # 销毁变量
        #             else:
        #                 continue
        #     if 'afterImages' in JSONlist[num] and len(imgList) < 10000:  # 若存在内容，并且内容条数少于4条
        #         wadePrint(JSONlist[num]['afterImages'])
        #         for imgNum in range(0, len(JSONlist[num]['afterImages'])):
        #             wadePrint(JSONlist[num]['afterImages'][imgNum])
        #             if 'imgUrl' in JSONlist[num]['afterImages'][imgNum]:  # 控制字符150以内
        #                 this_imgUrl = JSONlist[num]['afterImages'][imgNum]['imgUrl']
        #                 wadePrint(JSONlist[num]['afterImages'][imgNum]['imgUrl'])
        #                 # url统一修改函数：把里边的n0字符串替换，尺寸也替换掉 改成s720x540
        #                 if 'img30.360buyimg.com/n0/' in this_imgUrl:
        #                     this_imgUrl = this_imgUrl.replace("img30.360buyimg.com/n0/",
        #                                                       "img30.360buyimg.com/n1/")
        #                 if 's128x96_jfs/' in this_imgUrl:
        #                     this_imgUrl = this_imgUrl.replace("s128x96_jfs/", "s720x540_jfs/")
        #                 if '\n' in this_imgUrl:
        #                     this_imgUrl = this_imgUrl.replace('\n', '')
        #                 if '\r' in this_imgUrl:
        #                     this_imgUrl = this_imgUrl.replace('\r', '')
        #                 # if '//' in this_imgUrl:
        #                 #     this_imgUrl = this_imgUrl.replace("//", "")
        #                 imgList.append(this_imgUrl)
        #                 del this_imgUrl  # 销毁变量
        #             else:
        #                 continue
        #     else:
        #         continue
        #
        # wadePrint(f'京东爬虫程序结束,获取评论{len(commentList)}条，图片{len(imgList)}条')
        # # wadePrint(imgList)
        # random.shuffle(commentList)
        # random.shuffle(imgList)
        # # wadePrint(imgList)
        #
        # del content,json_flag,JSONlist
        # return commentList, imgList, '😆jdmain转换正常'  # 打乱重拍
        # # except Exception as e:
        # #     return [], [], '😅jdmain转换出错'


if __name__ == '__main__':
    # wordList,imgLIST,result = JDSpider().spider_Newcomment(10034589227536, 0)
    # wadePrint(wordList,imgLIST,result)
    # wadePrint(JDSpider().spider_itemByLeiMu("1319,1523,7054"))
    # wadePrint(JDSpider().spider_Newcomment(100021972412, 211111))
    # jdOBJ = JDSpider()
    # jdOBJ.jdSing()
    # for i in range(20):
    #
    #     # wadePrint(JDSpider().spider_Newcomment(100021972412, i,proxies=wadeTools_Agent.getAGENT()))
    #     wadePrint(JDSpider().spider_Newcomment(100021972412, i,wadeTools_Agent.getAgent()))
    #     # wadePrint(JDSpider().spider_itemQueston(100016086218))
    #     # wadePrint(max(len(s) for s in JDSpider().spider_itemQueston(100016086218)[0]['KEYS']))
    #     # wadePrint(max(JDSpider().spider_itemQueston(100016086218)[0]['KEYS'], key=len, default=''))


    # wadePrint(JDSpider().spider_Newcomment(10142124390094, 0))
    # a = JDSpider_Drissionpage().spider_itemQueston(10142124390094)    # a = JDSpider().spider_itspider_itemDataemBaiduSearch(10090874160408, 0)
    # wadePrint(a)
    print(JDSpider_Drissionpage().spider_itemBaiduSearch(keyword="联想小新笔记本"))