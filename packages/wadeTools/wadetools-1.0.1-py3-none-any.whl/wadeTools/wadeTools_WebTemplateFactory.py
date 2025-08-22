#!/usr/bin/env python
# coding=utf-8
# author:wade
# contact: 317909531@qq.com
# datetime:2021/1/2 21:41

"""
文件说明：基础类，生成模板使用
"""
import random


# 构造文章的基础,输入基本信息，构造出评论列表和图片列表
import time

from wadeTools.wadeTools_JDAPI import JDSpider
from wadeTools import wadeTools_baiduPost_API,wadeTools_ReadAndWrite
from wadeTools import wadeTools_error
from wadeTools.wadeTools_Print import wadePrint
#该类废弃
# class Tools_Template(object):
#     # 废弃
#     def __init__(self, title, commentList, imgList, itemURL, shopUrl, **kwargs):
#
#         """
#         本函数需要有6条评论和6个图片才能运行，在调用前需要做好判断
#
#         :param title: 生成文案的标题
#         :param commentList: 生成文案的评论列表
#         :param imgList: 生成文案的图片列表
#         :param itemURL: 自己的商品推广链接
#         :param shopUrl: 自己的店铺推广链接
#         :return 产出文章
#         :templateFactory_forDiscuz Return:主句字符串和评论列表
#         """
#         random.shuffle(commentList)
#         random.shuffle(imgList)
#         self.title = title
#         self.commentList = commentList
#         self.imgList = imgList
#         self.itemURL = itemURL
#         self.shopUrl = shopUrl
#         self.kwargs = kwargs
#         self.ifRun = True
#         self.pinglunList = []  # 论坛跟帖专用
#         self.content = ''  # 论坛跟帖专用
#         wadePrint(self.kwargs)
#
#     def wordJoin_imgJoin(self):
#         # 这个函数是处理的核心，输出的内容是一段一段的，[一组话，加上几张配图],后边只需要判断非空就行了
#         words = []
#         imgs = []
#         countWORD = 0
#
#         P = [1, 1, 1, 1, 1, 1, 1, 1]  # 文章段落排版，如果没有图片了，就不再进行编入
#         I = [1, 1, 1, 1, 1, 1, 1, 1]
#         # 第一次循环检查需求条数是否超出评论总量，如果不超出，就生成
#         # 第二次循环检查需求条数是否超出评论剩余，如果不超出，就生成
#         for runTime, num in enumerate(P):
#             if P[runTime] <= len(self.commentList) - countWORD:  # 检查组合后剩余条数
#                 # 根据要求进行循环
#                 # wadePrint('开始使用', (countWORD, countWORD + P[runTime]))
#                 words.append(''.join(self.commentList[countWORD:countWORD + P[runTime]]))  # 第0段
#                 # 统计已经用掉多少条
#                 countWORD = countWORD + num
#                 # wadePrint('剩余条数', len(self.commentList) - countWORD)
#
#
#         # 验证生产环境
#         articleList = []
#         imgLists = []
#         imgLists = self.imgList[2:].copy()
#         """
#             0 one
#             1 two
#             2 three
#         """
#         for cout, i in enumerate(words,start=0):
#             imgss = []
#             if len(I) > cout:
#                 # wadePrint(len(I),cout)
#
#                 for item in range(I[cout]):
#                     if imgLists != []:
#                         imgss.append(imgLists.pop(0))
#                     else:
#                         imgss = []
#             else:
#                 mgss = []
#             articleList.append([i, imgss])
#         return articleList
#
#     def templateFactory_forDiscuz(self,longUrl):
#         self.words = self.wordJoin_imgJoin()
#
#         # 主要内容：1段话，2张图片
#         # 如果只有一句话，没有图： 如果只有一句话 一张图：如果只有一句话2张图，如果只有1句话 3张图，如果只有2句话
#
#         if len(self.words) > 2 and len(self.imgList) >= 2:
#             self.content = f'''[font=&quot;]{self.words[0][0]}[/font]
#         [font=&quot;][b][size=4]关于产品质量怎么样，以下供参考：[/size][/b]
#         [/font][b][size=4][color=#ff0000]【千万不要被骗了】查看官网最新报价[/color][/size][/b][font=&quot;][color=#ff0000][size=4][b]：[/b][/size][/color][/font][font=arial, Tahoma, Verdana, STHeiTi, simsun, sans-serif, 宋体][size=5][color=#00bfff][b][url={longUrl}]点击查看[/url][/b][/color][/size][/font]
#         [font=&quot;][color=#ff0000][/color][/font][font=&quot;][color=#ff0000][size=4][b]产品性能，使用感受综合评测：[/b][/size][/color][/font][font=arial, Tahoma, Verdana, STHeiTi, simsun, sans-serif, 宋体][size=5][color=#00bfff][b][url={longUrl}]点击查看[/url][/b][/color][/size][/font]
#         [img=400,400]{self.imgList[0]}[/img]
#         [img=400,400]{self.imgList[1]}[/img]'''
#
#             for index, item in enumerate(self.words, start=1):
#                 pinglunWord = f'''[font=&quot]{item[0]}[/font]
#                 '''
#                 for imgRealLink in item[1]:
#                     pinglunWord = pinglunWord+f'''[img]{imgRealLink}[/img]
#                     '''
#                 self.pinglunList.append(pinglunWord)
#                 del pinglunWord
#
#             return self.content, self.pinglunList
#         else:
#             return [], []
#
#     def templateFactory_forQb(self,jdid,shopid,shopname,skuName,item_MainImg,item_price,shotUrl, longUrl):
#         self.words = self.wordJoin_imgJoin()
#         # 京东id/店铺id/店铺名称/产品名称/产品主图/产品价格/////
#         """返回self.content 字符串"""
#         if self.words != []:
#             self.content = f'''{self.words[0][0]}
#                         <p><strong><span style="font-size: big;color: black;">【千万不要被骗了】点击下方链接查看官网最新报价</span></strong></p>
#         <div>
#         <a style="background-color: #f6f6f6;
#           display: block;
#           border-radius: 8px;
#           box-shadow:0px 0px 10px 5px #aaa;
#           overflow: hidden;
#           color: inherit;
#           margin: 1em auto;
#           max-width: 100%;
#           min-height: 88px;
#           position: relative;
#           text-decoration: none;
#           width: 390px;
#           z-index: 0;"
#            href="{longUrl}">
#             <div style="-webkit-box-align: stretch;
#                 -ms-flex-align: stretch;
#                 align-items: stretch;
#                 position: relative;
#                 display: -webkit-box;
#                 display: -ms-flexbox;
#                 display: flex;
#                 overflow: hidden;
#                 max-width: 400px;
#                 min-height: 88px;">
#                 <div style="-webkit-box-sizing: border-box;
#                       box-sizing: border-box;
#                       width: 100%;
#                       padding: 14px;
#                       z-index: 2;
#                       -webkit-box-align: stretch;
#                       -ms-flex-align: stretch;
#                       align-items: stretch;
#                       position: relative;
#                       display: -webkit-box;
#                       display: -ms-flexbox;
#                       display: flex;">
#                     <div style="flex-shrink: 0;
#                             overflow: hidden;
#                             position: relative;
#                             border-radius: 6px;
#                             height: 100px;
#                             width: 100px;">
#                         <img style="height: 100%;
#                                   width: 100%;" src="{item_MainImg}"
#                              alt="">
#                     </div>
#                     <div style="
#                             display: -webkit-box;
#                             display: -ms-flexbox;
#                             display: flex;
#                             -webkit-box-orient: vertical;
#                             -webkit-box-direction: normal;
#                             -ms-flex-direction: column;
#                             flex-direction: column;
#                             -webkit-box-flex: 1;
#                             -ms-flex-positive: 1;
#                             flex-grow: 1;
#                             margin-left: 12px;
#                             overflow: hidden;">
#                         <div style="display: flex;-webkit-box-align: center;
#                                   -ms-flex-align: center;
#                                   align-items: center;
#                                   -webkit-box-pack: justify;
#                                   -ms-flex-pack: justify;
#                                   justify-content: space-between;">
#                             <div style="color: #121212;
#                                         font-size: 16px;
#                                         line-height: 20px;
#                                         max-height: 40px;
#                                         font-weight: 600;
#                                         font-synthesis: style;
#                                         display: -webkit-box;
#                                         text-overflow: ellipsis;
#                                         overflow: hidden;
#                                         -webkit-line-clamp: 2;
#                                         -webkit-box-orient: vertical;">{skuName}
#                             </div>
#                         </div>
#                         <div style="color: #646464;
#                               font-size: 12px;
#                               line-height: 17px;
#                               margin-top: 5px;
#                               font-weight: 600;
#                               font-synthesis: style;"> 京 东
#                         </div>
#                         <div style="display: -webkit-box;
#                               display: -ms-flexbox;
#                               display: flex;
#                               -webkit-box-align: end;
#                               -ms-flex-align: end;
#                               align-items: flex-end;
#                               margin-top: auto;">
#                             <div style="margin-right: auto;display: block;">
#                                 <div class="MCNLinkCard-price" style="-webkit-box-align: center;
#                               -ms-flex-align: center;
#                               align-items: center;
#                               color: #ff7955;
#                               display: -webkit-box;
#                               display: -ms-flexbox;
#                               display: flex;
#                               font-size: 16px;
#                               font-weight: 500;
#                               line-height: 18px;
#                               margin-right: auto;">
#                                     <span>¥ {item_price}</span></div>
#                             </div>
#                             <div style="display: -webkit-box;
#             display: -ms-flexbox;
#             display: flex;
#             -ms-flex-negative: 0;
#             flex-shrink: 0;
#             -webkit-box-pack: center;
#             -ms-flex-pack: center;
#             justify-content: center;
#             -ms-flex-item-align: start;
#             align-self: flex-start;
#             -webkit-box-align: center;
#             -ms-flex-align: center;
#             align-items: center;
#             color: #ff7955;
#             font-size: 13px;
#             height: 17px;
#             line-height: 17px;
#             font-weight: 600;
#             font-synthesis: style;" role="button">去购买
#                                 <span style="display: inline-flex; align-items: center;">&#8203;</span></div>
#                         </div>
#                     </div>
#                 </div>
#             </div>
#         </a>
#     </div>
# '''
#             for index, item in enumerate(self.words, start=1):
#                 for imgRealLink in item[1]:
#                     self.content = self.content + f'''<img style="height: 100%;
#                                   width: 100%;" src="{imgRealLink}" alt="" />'''
#                 self.content = self.content + f'''<p>{item[0]}</p>'''
#
#         return self.content
#
#     def templateFactory_forWeb(self,jdid=None,shopid=None,shopname=None,skuName=None,item_MainImg=None,item_price=None,shotUrl=None, longUrl=None,kword1=None,kword2=None):
#         return ''

class Tools_Template_New(object):
    """百家专用 """
    def templateFactory_forJDWeb(self,COOKIE,html_TEMPLATE,JDID=100016086218,pages=10):
        # 问答模板处理  非关键模块
        try:
            (askList) = JDSpider().spider_itemQueston(JDID)  # 爬取问答：
            askTemp,answersTmp = "",''
            for index, item in enumerate(askList):
                answersTmp=''
                if max(item['KEYS'], key=len, default='') == "":
                    continue
                # for answer in item['KEYS']:
                answersTmp = answersTmp+f"<p>♥{max(item['KEYS'], key=len, default='')}</p>"
                askTemp = askTemp+f"<li>问题：{item['QUESTION']}{answersTmp}</li>"
            askTemp = '''<div><ol>''' + askTemp + '''</ol></div>'''

            html_TEMPLATE = html_TEMPLATE.replace('【商品问答】', askTemp)  #替换模板 【问答模块】
        except:
            html_TEMPLATE = html_TEMPLATE.replace('【商品问答】', '')  # 替换模板 【问答模块】
            wadePrint('问答模块处理异常')

        # 爬取 商品详细参数 非关键模块
        goodName = ''
        try:
            (itemDataList) = JDSpider().spider_itemData(JDID)
            itemList = []

            for items in itemDataList:
                itemName = items[1]
                itemContent = items[2]
                if "href" in itemContent:
                    continue
                if "商品名称" in itemName:
                    goodName = items[2]
                itemList.append({"itemName": itemName, "itemContent": itemContent})
            detailTemp = ''
            for index, item in enumerate(itemList):
                detailTemp = detailTemp + f"<li>{item['itemName']}:{item['itemContent']}</li>"
            detailTemp = '''<div><ul>''' + detailTemp + '''</ul></div>'''

            html_TEMPLATE = html_TEMPLATE.replace('【商品详情】', detailTemp).replace('【商品名称】', goodName)  # 替换模板 【商品详情】
        except:
            wadePrint('商品详情参数失败')
            html_TEMPLATE = html_TEMPLATE.replace('【商品详情】', '')  # 替换模板 【商品详情】

        # 爬虫类初始化，获取图片和评论列表   获取图文列表 commentList imgList

        commentList, imgList, comments_p, imglists_p = [], [], [], []

        for i in range(0, pages):  # 爬0到PAGE要求页，超过10条就结束
            comments_p, imglists_p, results = JDSpider().spider_Newcomment(JDID, i)
            commentList.extend(comments_p)
            imgList.extend(imglists_p)
            if len(commentList) >= 10 and len(imgList) >= 10:
                random.shuffle(commentList)  # 打乱
                random.shuffle(imgList)  # 打乱
                commentList = commentList[0:7]
                imgList = imgList[0:7]
                break


        """图片转百家链接："""
        newIMGlist =[]
        for img in imgList[::-1]:  # 转换图片为Baidu链接,转换失败就去掉这个链接
            responseImgUrl = wadeTools_baiduPost_API.baiduImageUrl(imageURL='http:' + img,COOKIE=COOKIE)
            newIMGlist.append(responseImgUrl)
            # if responseImgUrl=='':  #转换失败
            #     imgList.remove(img)
        imgList = newIMGlist

        if len(imgList)==0:
            imgList.append('https://pic.rmb.bdstatic.com/bjh/down/17cdd4a0e921b469b7cf724472888c3c.jpeg') # 加个假封面

        commentList = commentList.__iter__()
        iterimgList = imgList.__iter__()
        html_TEMPLATE = html_TEMPLATE.replace('?', '')
        html_TEMPLATE = html_TEMPLATE.replace('【评论一】', next(commentList,"")).replace('【图片一】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论二】', next(commentList,"")).replace('【图片二】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论三】', next(commentList,"")).replace('【图片三】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论四】', next(commentList,"")).replace('【图片四】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论五】', next(commentList,"")).replace('【图片五】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论六】', next(commentList,"")).replace('【图片六】',next(iterimgList,""))
        wadePrint(html_TEMPLATE)
        wadePrint("文章组合成功")

        return html_TEMPLATE,imgList[0],goodName

    def templateFactory_forJDWeb_Simple(self,html_TEMPLATE,JDID=100016086218,pages=10,waitTime=0.05):
        """纯京东发帖专用 """
        try:
            (askList) = JDSpider().spider_itemQueston(JDID)  # 爬取问答：
            time.sleep(waitTime)
            askTemp,answersTmp = "",''
            for index, item in enumerate(askList):
                answersTmp=''
                if max(item['KEYS'], key=len, default='') == "":
                    continue
                # for answer in item['KEYS']:
                answersTmp = answersTmp+f"<p>♥{max(item['KEYS'], key=len, default='')}</p>"
                askTemp = askTemp+f"<li>问题：{item['QUESTION']}{answersTmp}</li>"
            askTemp = '''<div><ol>''' + askTemp + '''</ol></div>'''

            html_TEMPLATE = html_TEMPLATE.replace('【商品问答】', askTemp)  #替换模板 【问答模块】
        except:
            html_TEMPLATE = html_TEMPLATE.replace('【商品问答】', '')  # 替换模板 【问答模块】
            wadePrint('问答模块处理异常')

        # 爬取 商品详细参数 非关键模块
        goodName = ''
        try:
            itemDataList = JDSpider().spider_itemData(JDID)
            time.sleep(waitTime)
            itemList = []

            for items in itemDataList:
                itemName = items[1]
                itemContent = items[2]
                if "href" in itemContent:
                    continue
                if "商品名称" in itemName:
                    goodName = items[2]
                itemList.append({"itemName": itemName, "itemContent": itemContent})
            detailTemp = f'''<table border="1"> 
                    {''.join([f"<tr><td>{item['itemName']}</td> <td>{item['itemContent']}</td></tr>" for item in itemList])}
                </table>'''

            html_TEMPLATE = html_TEMPLATE.replace('【商品详情】', detailTemp).replace('【商品名称】', goodName)  # 替换模板 【商品详情】
        except:
            wadePrint('商品详情参数失败')
            html_TEMPLATE = html_TEMPLATE.replace('【商品详情】', '')  # 替换模板 【商品详情】

        # 爬虫类初始化，获取图片和评论列表   获取图文列表 commentList imgList
        commentList, imgList, comments_p, imglists_p = [], [], [], []

        for i in range(0, pages):  # 爬0到PAGE要求页，超过10条就结束
            time.sleep(waitTime)
            comments_p, imglists_p, results = JDSpider().spider_Newcomment(JDID, i)
            commentList.extend(comments_p)
            imgList.extend(imglists_p)
            if len(commentList) >= 8 and len(imgList) >= 8:
                random.shuffle(commentList)  # 打乱
                random.shuffle(imgList)  # 打乱
                commentList = commentList[0:7]
                imgList = imgList[0:7]
                break
        imgList = [f"http:{img}" for img in imgList]



        commentList = commentList.__iter__()
        iterimgList = imgList.__iter__()
        html_TEMPLATE = html_TEMPLATE.replace('?', '')
        html_TEMPLATE = html_TEMPLATE.replace('【评论一】', next(commentList,"")).replace('【图片一】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论二】', next(commentList,"")).replace('【图片二】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论三】', next(commentList,"")).replace('【图片三】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论四】', next(commentList,"")).replace('【图片四】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论五】', next(commentList,"")).replace('【图片五】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论六】', next(commentList,"")).replace('【图片六】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论七】', next(commentList,"")).replace('【图片七】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论八】', next(commentList,"")).replace('【图片八】',next(iterimgList,""))
        html_TEMPLATE = html_TEMPLATE.replace('【商品ID】', str(JDID))
        wadePrint(html_TEMPLATE)
        wadePrint("文章组合成功")
        if len(imgList)==0:
            # 说明没有任何图片
            raise wadeTools_error.Error_break(f"{JDID}商品无封面图，价格返回的是空值，无推广价值")
        return html_TEMPLATE,imgList[0],goodName,imgList

    def templateFactory_forJDWeb_AI(self,html_TEMPLATE, JDID=100016086218, pages=10):
        from wadeTools import wadeTools_dataoke_API, wadeTools_readConfig_ini,wadeTools_ReadAndWrite
        """OPEN ai"""
        # 通过ID获取大淘客推广链接：

        # 绝对路径
        Ini_Data = wadeTools_readConfig_ini.ReadConfig('大淘客配置.ini')
        # runNumNow = Ini_Data.get_param('USER', "runNumNow")
        '''大淘客配置文件初始化和读取'''
        materialId = f'https://item.jd.com/{JDID}.html'
        appKey = Ini_Data.get_param('USER', "appKey")
        appSecret = Ini_Data.get_param('USER', "appSecret")
        version = Ini_Data.get_param('USER', "version")
        unionId = Ini_Data.get_param('USER', "unionId")
        aiopen1close0 = Ini_Data.get_param('USER', "aiopen1close0")
        # gptWord = Ini_Data.get_param('USER', "aiopen1close0")

        # if appKey == "" or appSecret == "" or version == "" or unionId == "" or aiopen1close0=='':
        #     Ini_Data.setItem('USER', "appKey", "jd的appk")  # 修改
        #     Ini_Data.setItem('USER', "appSecret", "jd的appSecret")  # 修改
        #     Ini_Data.setItem('USER', "version", "v1.0.1")  # 修改
        #     Ini_Data.setItem('USER', "unionId", "推广者id")  # 修改
        #     Ini_Data.setItem('USER', "aiopen1close0", "1")  # 修改
        # Ini_Data.saveIni('大淘客配置.ini')  # 保存


        try:
            # 获取价格和商品图第一张
            item_detailJson = wadeTools_dataoke_API.get_dtk_detail(skuIds=JDID, appKey=appKey, appSecret=appSecret,
                                                                   version=version).json()
            # wadePrint(item_detailJson)  # 打印商品详情
            if "网络请求失败" in str(item_detailJson):
                wadePrint("网络请求失败")

        except Exception as e:
            wadePrint("请求出错，检查本段代码",e)
            raise wadeTools_error.Error_break(f"{JDID}请求出错")
        try:
            from wadeTools import wadeTools_UserJSON
            actualPrice = wadeTools_UserJSON.get_dict_by_key(will_find_dist=item_detailJson, find_keys='actualPrice')
            detailImages = wadeTools_UserJSON.get_dict_by_key(will_find_dist=item_detailJson, find_keys='detailImages')[0]
            dataokegoodName = wadeTools_UserJSON.get_dict_by_key(will_find_dist=item_detailJson, find_keys='skuName')
            # wadePrint(actualPrice, detailImages)
            int(actualPrice)  # 测试商品是否有效
        except Exception as e:
            wadePrint("商品失效，无法获取详细信息",e)
            raise wadeTools_error.Error_break(f"{JDID}商品失效，价格返回的是空值，无推广价值")

        try:
            askList = JDSpider().spider_itemQueston(JDID)  # 爬取问答：
            askTemp, answersTmp = "", ''
            for index, item in enumerate(askList):
                answersTmp = ''
                if max(item['KEYS'], key=len, default='') == "":
                    continue
                # for answer in item['KEYS']:
                answersTmp = answersTmp + f"<p>♥{max(item['KEYS'], key=len, default='')}</p>"
                askTemp = askTemp + f"<li>问题：{item['QUESTION']}{answersTmp}</li>"
            askTemp = '''<div><ol>''' + askTemp + '''</ol></div>'''

            html_TEMPLATE = html_TEMPLATE.replace('【商品问答】', askTemp)  # 替换模板 【问答模块】
        except:
            html_TEMPLATE = html_TEMPLATE.replace('【商品问答】', '')  # 替换模板 【问答模块】
            wadePrint('问答模块处理异常')


        # wadePrint(Ini_Data.getFilepath())

        # myShopLink = wadeTools_dataoke_API.getMyLink(materialId=materialId,appKey=appKey,appSecret=appSecret,version=version,unionId=unionId)
        # wadePrint(myShopLink)
        try:
            myShopLink = wadeTools_dataoke_API.getMyLink(materialId=materialId, appKey=appKey, appSecret=appSecret, version=version,unionId=unionId,limitLength=200)
            wadePrint(myShopLink)
        except:
            abc=input("请配置大淘客参数后继续运行，参数不用加引号")
            myShopLink = \
            wadeTools_dataoke_API.getMyLink(materialId=materialId, appKey=appKey, appSecret=appSecret, version=version,
                                            unionId=unionId,limitLength=200)
            wadePrint(myShopLink)

        # 爬取 商品详细参数 非关键模块
        goodName = dataokegoodName
        try:
            itemDataList = JDSpider().spider_itemData(JDID)
            itemList = []

            for items in itemDataList:
                itemName = items[1]
                itemContent = items[2]
                if "href" in itemContent:
                    continue
                # if "商品名称" in itemName:
                #     goodName = items[2]
                itemList.append({"itemName": itemName, "itemContent": itemContent[0:20]})
            detailTemp = f'''<p>{''.join([f"<li>{item['itemName']}:{item['itemContent']}</li>" for item in itemList])}</p>'''   # li模式
            # detailTemp = f'''<table>{''.join([f"<tr><td>{item['itemName']}</td>:<td>{item['itemContent']}</td></tr>" for item in itemList])}</table>'''  # 表格模式

        except:
            wadePrint('商品详情参数失败')
            detailTemp=''
            html_TEMPLATE = html_TEMPLATE.replace('【商品详情】', '')  # 替换模板 【商品详情】
        html_TEMPLATE = html_TEMPLATE.replace('【商品详情】', detailTemp).replace('【商品名称】', goodName)  # 替换模板 【商品详情】

        # 爬虫类初始化，获取图片和评论列表   获取图文列表 commentList imgList
        commentList, imgList, comments_p, imglists_p = [], [], [], []

        for i in range(0, pages):  # 爬0到PAGE要求页，超过10条就结束
            comments_p, imglists_p, results = JDSpider().spider_Newcomment(JDID, i)
            commentList.extend(comments_p)
            imgList.extend(imglists_p)
            if len(comments_p)==0 and len(imglists_p)==0:  #最热评论都是0的话就结束
                break
            if len(commentList) >= 4 and len(imgList) >= 4:
                random.shuffle(commentList)  # 打乱
                random.shuffle(imgList)  # 打乱
                break
        imgList = [f"http:{img}" for img in imgList]
        wadePrint(f"共获取图片{len(imgList)}张，评论{len(commentList)}条")
        commentList = commentList.__iter__()
        iterimgList = imgList.__iter__()




        # 多进程

        # AI 模板图片3张，评论4个
        str1 = next(commentList, "")
        str2 = next(commentList, "")
        # str3 = next(commentList, "")
        # wadePrint(str1, '\n', str2)
        try:
            if aiopen1close0 == '0':
                raise Exception
            else:
                AI_1 = str1
                AI_2 = str2
        except:
            AI_1 =str1
            AI_2 =str2
            # AI_3 =str3
        if "作为一个人工智能语言模型，我无法提供此类信息" in AI_1:
            AI_1 = str1
        if "作为一个人工智能语言模型，我无法提供此类信息" in AI_2:
            AI_2 =str2
        # if "作为一个人工智能语言模型，我无法提供此类信息" in AI_3:
            # AI_3 =str3
        # if "作为一个人工智能语言模型，我无法提供此类信息" in AI_1 or "ip一小时内连续请求了300次以上已" in AI_2 or "ip一小时内连续请求了300次以上已" in AI_2:
        #     wadePrint("次数用完")
        #     AI_1 = str1
        #     AI_2 = str2
        #     AI_3 = str3
        #     wadePrint("AI次数不够了，请更换IP继续，否则请直接退出，按回车继续。。不换账号继续会影响文章质量")
        #
        #     raise wadeTools_error.Error_break("AI次数不够了，请更换IP继续，否则请直接退出，按回车继续。。不换账号继续会影响文章质量")
            # time.sleep(999999)
        # 百度长尾词

        baiduLongWords = wadeTools_dataoke_API.baiduXiaLaWords(goodName).__iter__()
        wadePrint("百度下拉词")
        wadePrint(baiduLongWords)

        html_TEMPLATE = html_TEMPLATE.replace('?', '')
        html_TEMPLATE = html_TEMPLATE.replace('【AI语句评测1】', AI_1).replace('【图片一】', next(iterimgList, ""))
        html_TEMPLATE = html_TEMPLATE.replace('【AI语句评测2】', AI_2).replace('【图片二】', next(iterimgList, ""))
        html_TEMPLATE = html_TEMPLATE.replace('【图片三】', next(iterimgList, ""))
        html_TEMPLATE = html_TEMPLATE.replace('【评论四】', next(commentList, "")).replace('【图片四】', next(iterimgList, ""))
        html_TEMPLATE = html_TEMPLATE.replace('【商品ID】', str(JDID))
        html_TEMPLATE = html_TEMPLATE.replace('【商品推广链接】',myShopLink)
        wadePrint("百度下拉词sing1")
        if int(actualPrice)>=150:
            actualPrice = int(actualPrice)
        else:
            actualPrice=int(actualPrice)


        html_TEMPLATE = html_TEMPLATE.replace('【商品价格】',str(actualPrice))
        html_TEMPLATE = html_TEMPLATE.replace('【商品封面】',detailImages)
        html_TEMPLATE = html_TEMPLATE.replace('【文章标题】',f'{goodName[0:24]}{wadeTools_ReadAndWrite.lunxunTxt("标题后缀.txt")}')
        html_TEMPLATE = html_TEMPLATE.replace('【商品名称】',f'{goodName[0:24]}')
        html_TEMPLATE = html_TEMPLATE.replace('【商品卡片名称】',f'{goodName[0:24]}')
        wadePrint("百度下拉词sing2")
        html_TEMPLATE = html_TEMPLATE.replace('【轮链1】',f'{wadeTools_ReadAndWrite.lunxunTxt("./发帖结果/发布成功文章记录.txt")}')
        html_TEMPLATE = html_TEMPLATE.replace('【轮链2】',f'{wadeTools_ReadAndWrite.lunxunTxt("./发帖结果/发布成功文章记录.txt")}')
        wadePrint("百度下拉词sing3")
        html_TEMPLATE = html_TEMPLATE.replace('【轮链3】',f'{wadeTools_ReadAndWrite.lunxunTxt("./发帖结果/发布成功文章记录.txt")}')
        html_TEMPLATE = html_TEMPLATE.replace('【百度长尾词】',f'{next(baiduLongWords,"")}')
        # wadePrint(html_TEMPLATE)
        wadePrint("文章组合成功")
        if len(imgList)==0:
            imgList.append(detailImages)
        wadePrint(imgList)
        wadePrint(imgList[0], goodName,JDID)
        return html_TEMPLATE, imgList[0], goodName


if __name__ == '__main__':
    # #百家发帖流程
    html_TEMPLATE ='''<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
    <span>
        <strong style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
        前言
        </strong>
    </span>
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      <span style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      &nbsp;&nbsp;&nbsp;&nbsp;&#8203;所有具备超赞的旗舰产品，自然是将用户体验全部拉满，精美工艺、质量口碑上上选、回血迅速…这些属性可一样也不能少，【商品名称】可以说是我们生活中“超亲密”的产品了。现在的产品细分市场太激烈了,很多人在选择上还是选择“感性”，性急的稀里糊涂的被动入手了。那刚好最近正在研究这款【商品名称】，今天就让笔者带大家尽情领悟它的不凡实力吧。
      </span>
</p>
<p>
	<img src="【图片一】" alt="" />
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
    <span>
        <strong style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
        设计：匠心独具
        </strong>
    </span>
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      <span style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      &nbsp;&nbsp;&nbsp;&nbsp;&#8203;本次到手的【商品名称】，【评论一】
      </span>
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      <span style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      &nbsp;&nbsp;&nbsp;&nbsp;&#8203;觉得不错的话可以到官网看看商品参数，我已经给大家找到了官方的详情，不想浪费时间的可以入手啦
      </span>
</p>
<div id="商品卡" ></div>
<div id="商品问答" ></div>
热度评分：【热度评分】分


印象评分：【印象评分】分


综合评分：【综合评分】分
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
    <span>
        <strong style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
        产品参数指标
        </strong>
    </span>
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      <span style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      &nbsp;&nbsp;&nbsp;&nbsp;&#8203;【评论二】
      </span>
</p>
<p>
	<img src="【图片二】" alt="" />
</p>
【商品参数】
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
    <span>
        <strong style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
        网友关注的【商品名称】问题
        </strong>
    </span>
</p>
【商品问答】
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
    <span>
        <strong style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
        网友贴心反馈
        </strong>
    </span>
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      <span style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      &nbsp;&nbsp;&nbsp;&nbsp;&#8203;【评论三】
      </span>
</p>
<p>
	<img src="【图片三】" alt="" />
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      <span style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      &nbsp;&nbsp;&nbsp;&nbsp;&#8203;【评论四】
      </span>
</p>
<p>
	<img src="【图片四】" alt="" />
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      <span style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      &nbsp;&nbsp;&nbsp;&nbsp;&#8203;【评论五】
      </span>
</p>


<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
    <span>
        <strong style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box">
        结语
        </strong>
    </span>
</p>
<p style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      <span style="margin: 0px;padding: 0px;border: 0px;outline: 0px;vertical-align: initial;background: 0px 0px;-webkit-tap-highlight-color: transparent;max-width: 100%;overflow-wrap: break-word;box-sizing: border-box" >
      &nbsp;&nbsp;&nbsp;&nbsp;&#8203;经过笔者全方位的体验，【商品名称】表现真的赞啊。这么好的产品无论是在家用还是送亲朋好友，都能很好的，笔者决定自己留着用了嘎嘎。以上是【商品名称】使用过程中的体会，如果这次的分享文章对你有的选择有所帮助，记得点个赞支持哦~。
      </span>
</p>
'''
    wadePrint(Tools_Template_New().templateFactory_forJDWeb_AI(html_TEMPLATE=html_TEMPLATE,JDID=100016086218,pages=20)[0])


