#coding:utf-8
import json
import random
from urllib.parse import urlparse  #正则url标准库
import re
from urllib import parse
from wadeTools import wadeTools_Request, wadeTools_UserJSON, wadeTools_ReadAndWrite, wadeTools_Text,wadeTools_error
import requests
import time

#LOCAL 提交模板
SHOP_CARD_CODE ="""{"id":"【gid】","iframeSrc":"//baijiahao.baidu.com/builder/author/static/goods?id=【gid】","goodsType":"jingdong","original_title":"【title】","new_title":"【new_title】","image_list":[{"src":"【image_list】"}],"num_id":【num_id】,"price":"【price】","amout":"【num_id】","slink":"【slink】","original_price":0,"platform":"【platformName】","gid":"【gid】","commission":"【commission】","type":"news","saleCount":"【saleNum】","TPName":"","goods_prompt":""}"""
SHOP_CARD_WEB_CODE = """<p><br></p><p contenteditable="false" class="goods-iframe-wrapper"><iframe data-bjh-box="goods" data-goods-type="jingdong" data-goods-id="【gid】" data-goods-num_id="【num_id】" scrolling="no" frameborder="0" src="//baijiahao.baidu.com/builder/author/static/goods?id=【gid】" data-bjh-params="【商品卡源码】" class="edui-faked-goods" data-diagnose-id="174dd570c36379a49153045dfe2fa74d"></iframe></p><p><br></p>"""
SHOP_IMG_URL = """[{"src":"【图片链接】"}]"""
ARTICLE_IMG = """[{"src":"【图片一】@c_1,w_843,h_562,x_0,y_135","cropData":{"x":0,"y":135,"width":843,"height":562},"machine_chooseimg":1,"isLegal":0},{"src":"【图片二】@c_1,w_414,h_276,x_0,y_310","cropData":{"x":0,"y":310,"width":414,"height":276},"machine_chooseimg":1,"isLegal":0},{"src":"【图片三】@c_1,w_540,h_360,x_0,y_124","cropData":{"x":0,"y":124,"width":540,"height":360},"machine_chooseimg":1,"isLegal":0}]"""
ARTICLE_IMG_MAP = """[{"src":"【图片一】@c_1,w_843,h_562,x_0,y_135","origin_src":"【图片一】@wm_2,t_55m+5a625Y+3L+Wlvei0p+WTpQ==,fc_ffffff,ff_U2ltSGVp,sz_22,x_14,y_14"},{"src":"【图片二】@c_1,w_414,h_276,x_0,y_310","origin_src":"【图片二】@wm_2,t_55m+5a625Y+3L+Wlvei0p+WTpQ==,fc_ffffff,ff_U2ltSGVp,sz_11,x_7,y_7"},{"src":"【图片三】@c_1,w_540,h_360,x_0,y_124","origin_src":"【图片三】@wm_2,t_55m+5a625Y+3L+Wlvei0p+WTpQ==,fc_ffffff,ff_U2ltSGVp,sz_14,x_9,y_9"}]"""
IMAGE_LIST =[]
FENGMIAN_IMGR_URL =''
#获取全局变量：
# COOKIE=wadeTools_gol.get_value('COOKIE') #基础配置
# TOKEN=wadeTools_gol.get_value('TOKEN')  #基础百家toke
# PUBLIST_NUM=wadeTools_gol.get_value('PUBLIST_NUM')
# SHOP_CARD_CODE=wadeTools_gol.get_value('SHOP_CARD_CODE')
# SHOP_CARD_WEB_CODE=wadeTools_gol.get_value('SHOP_CARD_WEB_CODE')
# SHOP_IMG_URL=wadeTools_gol.get_value('SHOP_IMG_URL')
# ARTICLE_IMG=wadeTools_gol.get_value('ARTICLE_IMG')
# ARTICLE_IMG_MAP=wadeTools_gol.get_value('ARTICLE_IMG_MAP')
# IMAGE_LIST=wadeTools_gol.get_value('IMAGE_LIST') #本页面变量

#本地变量

# TITLE=wadeTools_gol.get_value('TITLE')
# CONTENT=wadeTools_gol.get_value('CONTENT')
# ABSTRACT=wadeTools_gol.get_value('ABSTRACT')
# ITEM_ID=wadeTools_gol.get_value('ITEM_ID',100028103960)



'''百度初始化'''
def baiduInit(COOKIE):


    url = 'https://baijiahao.baidu.com/builder/app/appinfo?'
    html = wadeTools_Request.wade_Request_get(url, addHeader={"Cookie": COOKIE})
    htmlDict = html.json()
    #print(htmlDict)
    #name = wadeTools_UserJSON.get_dict_by_key(htmlDict,'22222')
    errno = wadeTools_UserJSON.get_dict_by_key(htmlDict,'ext_info')
    location = wadeTools_UserJSON.get_dict_by_key(htmlDict,'location')
    app_level_desc = wadeTools_UserJSON.get_dict_by_key(htmlDict,'app_level_desc')
    app_id = wadeTools_UserJSON.get_dict_by_key(htmlDict,'app_id')
    # print(htmlDict)
    global PUBLIST_NUM
    PUBLIST_NUM = wadeTools_UserJSON.get_dict_by_key(htmlDict,'publish_num')
    uname = wadeTools_UserJSON.get_dict_by_key(htmlDict,'uname')
    domain = wadeTools_UserJSON.get_dict_by_key(htmlDict,'domain')
    return uname,PUBLIST_NUM
'''转换外链图片为百度图片'''
def baiduImageUrl(COOKIE,imageURL = 'https://pica.zhimg.com/50/v2-f78f790008da504b230ea3c28f8ef62e_720w.jpg?source=1940ef5c'):

    '''转换外链图片为百度图片'''
    # imageURL = 'https://pica.zhimg.com/50/v2-f78f790008da504b230ea3c28f8ef62e_720w.jpg?source=1940ef5c'
    url = f'https://baijiahao.baidu.com/builderinner/api/content/file/image/dump?usage=content&article_type=news&is_waterlog=1&url={imageURL}'  # 旧版转链
    url = f'https://baijiahao.baidu.com/pcui/picture/dumpproxy?usage=content&article_type=news&is_waterlog=1&url={imageURL}'
    html = wadeTools_Request.wade_Request_get(url, addHeader={"Cookie": COOKIE})
    htmlDict = html.json()
    print(htmlDict)

    try:
        # 参数保存
        bos_url = htmlDict['data']['bos_url']  # 水印链接
        # no_waterlog_bos_url = htmlDict['data']['no_waterlog_bos_url']  # 无水印链接
        # mime = htmlDict['data']['mime']  # 类型
        # height = htmlDict['data']['height']  # 高
        # width = htmlDict['data']['width']  # 宽
        # error_code = htmlDict['error_code']  # 错误码 0
        # error_msg = htmlDict['error_msg']  # 状态：success
        # errno = htmlDict['errno']  # 0
        print("url换链成功")
        return bos_url
    except Exception as e:
        print(e)
        print("imageURL转百度链接转换失败了")
        return ''

'''获取商品sign标识'''
def baidu_getShop_sign(COOKIE):
    url = 'https://cecom.baidu.com/m/shop/sdk/choosegoods/'
    html = wadeTools_Request.wade_Request_get(url,addHeader={"Cookie": COOKIE})

    #获取html中的js文件地址
    js_urlList = wadeTools_Request.get_Request_JsFiles(html.text)
    if len(js_urlList)>0:
        for jsURL in js_urlList:
            # print(jsURL)
            jshtml = wadeTools_Request.wade_Request_get(jsURL, addHeader={"Cookie": COOKIE})
            # print(jshtml.text)
            if '/proxy/select/search_goods?access_name=cecom_fe&ak=cecom_fe&sign=' in jshtml.text:
                js_sign = wadeTools_Text.wade_match_MiddleText(A='/proxy/select/search_goods\?access_name=cecom_fe&ak=cecom_fe&sign=',B ='"',content =jshtml.text)
                wadeTools_ReadAndWrite.wadeDownloadFile(filePath='1',fileName=f'123.js',html=jshtml)  #下载没用了
                return js_sign[0]

def baidu_selectShopItem(COOKIE,ITEM_ID):
    SHOP_CARD_CODE = """{"id":"【gid】","iframeSrc":"//baijiahao.baidu.com/builder/author/static/goods?id=【gid】","goodsType":"jingdong","original_title":"【title】","new_title":"【new_title】","image_list":[{"src":"【image_list】"}],"num_id":【num_id】,"price":"【price】","amout":"【num_id】","slink":"【slink】","original_price":0,"platform":"【platformName】","gid":"【gid】","commission":"【commission】","type":"news","saleCount":"【saleNum】","TPName":"","goods_prompt":""}"""
    SHOP_CARD_WEB_CODE = """<p><br></p><p contenteditable="false" class="goods-iframe-wrapper"><iframe data-bjh-box="goods" data-goods-type="jingdong" data-goods-id="【gid】" data-goods-num_id="【num_id】" scrolling="no" frameborder="0" src="//baijiahao.baidu.com/builder/author/static/goods?id=【gid】" data-bjh-params="【商品卡源码】" class="edui-faked-goods" data-diagnose-id="174dd570c36379a49153045dfe2fa74d"></iframe></p><p><br></p>"""

    # global newTitle,title
    url = f'https://cecom.baidu.com/proxy/select/search_goods?access_name=cecom_fe&ak=cecom_fe&sign={baidu_getShop_sign(COOKIE)}'
    # print(url)
    html = wadeTools_Request.wade_Request_post(url=url,addHeader={'Accept': 'application/json',"Cookie": COOKIE,'Content-Type': 'application/json;charset=utf-8'},data=json.dumps({"keyWord":f"https://item.jd.com/{ITEM_ID}.html","categoryId1":0}))
    print(html.json())
    available = wadeTools_UserJSON.get_dict_by_key(find_keys='available',will_find_dist=html.json())
    commission = wadeTools_UserJSON.get_dict_by_key(find_keys='commission',will_find_dist=html.json())
    commission_rate = wadeTools_UserJSON.get_dict_by_key(find_keys='commission_rate',will_find_dist=html.json())
    coupon = wadeTools_UserJSON.get_dict_by_key(find_keys='coupon',will_find_dist=html.json())
    goods_id = wadeTools_UserJSON.get_dict_by_key(find_keys='goods_id',will_find_dist=html.json())
    imageList = wadeTools_UserJSON.get_dict_by_key(find_keys='imageList',will_find_dist=html.json())[0]
    is_commission = wadeTools_UserJSON.get_dict_by_key(find_keys='is_commission',will_find_dist=html.json())
    num_id = wadeTools_UserJSON.get_dict_by_key(find_keys='num_id',will_find_dist=html.json())
    originalGoodsId = wadeTools_UserJSON.get_dict_by_key(find_keys='originalGoodsId',will_find_dist=html.json())
    originalTitle = wadeTools_UserJSON.get_dict_by_key(find_keys='originalTitle',will_find_dist=html.json())
    platform = wadeTools_UserJSON.get_dict_by_key(find_keys='platform',will_find_dist=html.json())
    platformName = wadeTools_UserJSON.get_dict_by_key(find_keys='platformName',will_find_dist=html.json())
    price = wadeTools_UserJSON.get_dict_by_key(find_keys='price',will_find_dist=html.json())
    real_platform = wadeTools_UserJSON.get_dict_by_key(find_keys='real_platform',will_find_dist=html.json())
    saleNum = wadeTools_UserJSON.get_dict_by_key(find_keys='saleNum',will_find_dist=html.json())
    slink = wadeTools_UserJSON.get_dict_by_key(find_keys='slink',will_find_dist=html.json())
    title = wadeTools_UserJSON.get_dict_by_key(find_keys='title',will_find_dist=html.json())
    originalPrice="0"
    ubcPlatform="all"
    tab="goodsMall"
    query = slink
    fromdata = "baiduboxapp"
    newTitle = title[0:50]
    v="1.1"


    #提交商品
    url = "https://cecom.baidu.com/creator/dhGoodsAdd"
    postFORM = {
    "TPName": "",
    "activityName": "",
    "available": available,
    "commission": commission,
    "commission_rate": commission_rate,
    "coupon": coupon,
    "from": fromdata,
    "goods_id": goods_id,
    "imageList": imageList,
    "is_commission":is_commission,
    "newTitle": newTitle,
    "num_id": num_id,
    "originalGoodsId": originalGoodsId,
    "originalPrice": originalPrice,
    "originalTitle": originalTitle,
    "platform": platform,
    "platformName": platformName,
    "price": price,
    "query": query,
    "rankName": "",
    "real_platform": real_platform,
    "saleNum": saleNum,
    "slink": slink,
    "tab": tab,
    "title": title,
    "tpName": "",
    "ubcPlatform": ubcPlatform,
    "v": "1.1",

}

    html = wadeTools_Request.wade_Request_post(url=url,addHeader={"Referer": "https://cecom.baidu.com/m/shop/sdk/choosegoods/","Host": "cecom.baidu.com","Accept": "application/json","Content-Type": "application/x-www-form-urlencoded; charset=utf-8","Cookie": COOKIE},data=postFORM)


    print(postFORM)



    gid = wadeTools_UserJSON.get_dict_by_key(find_keys='gid',will_find_dist=html.json())
    #修改商品卡模板源码
    # global SHOP_CARD_CODE,SHOP_CARD_WEB_CODE
    SHOP_CARD_CODE = SHOP_CARD_CODE.replace('【gid】',gid).replace('【title】',title).replace('【new_title】',newTitle).replace('【image_list】',imageList).replace('【num_id】',num_id)
    SHOP_CARD_CODE = SHOP_CARD_CODE.replace('【price】',str(price)).replace('【slink】',str(slink)).replace('【platformName】',str(platformName)).replace('【commission】',str(commission)).replace('【saleNum】',str(saleNum))

    SHOP_CARD_WEB_CODE = SHOP_CARD_WEB_CODE.replace('【gid】',str(gid)).replace('【num_id】',str(num_id)).replace('【商品卡源码】',parse.quote(safe="",string=SHOP_CARD_CODE)).replace('【gid】',str(gid))
    # print("打印商品卡")
    # print(SHOP_CARD_CODE)
    # print("打印商品卡网页代码")
    # print(SHOP_CARD_WEB_CODE)
    print("生成商品卡...成功")
    return SHOP_CARD_WEB_CODE
'''发帖功能模块'''
def baiduPostContent(TITLE,CONTENT,COVER_IMG,COOKIE,TOKEN,ABSTRACT):
    # exit(code=0)
    from urllib import parse

    # exit(0)
    formData = {
        'type': 'news',
        'title': TITLE[0:30],
        'content': CONTENT,
        'abstract': ABSTRACT,
        'len': 27917,
        'activity_list%5B0%5D%5Bid%5D': 408,
        'activity_list%5B0%5D%5Bis_checked%5D': 1,
        'source_reprinted_allow': 0,
        'original_status': 0,
        'original_handler_status': 1,
        'isBeautify': 'false',
        'cover_layout': 'one',
        # 'cover_images': '''[{"src":"https://pic.rmb.bdstatic.com/bjh/news/95950f5a98b8b4346e386ba63f29e650.jpeg?x-bce-process=image/crop,w_719,h_479,x_0,y_16","cropData":{"x":0,"y":16,"width":719,"height":479},"machine_chooseimg":1,"isLegal":0}]''',
        'cover_images': f'''[{{"src":"{COVER_IMG}","cropData":{{"x":0,"y":16,"width":626,"height":417}},"machine_chooseimg":1,"isLegal":0}}]''',
        # '_cover_images_map':f"""[{"src":"https://pica.zhimg.com/50/v2-f78f790008da504b230ea3c28f8ef62e_720w.jpg?x-bce-process=image/crop,w_719,h_479,x_0,y_16","origin_src":"https://pic.rmb.bdstatic.com/bjh/news/95950f5a98b8b4346e386ba63f29e650.jpeg?x-bce-process=image/watermark,bucket_baidu-rmb-video-cover-1,image_YmpoL25ld3MvNjUzZjZkMjRlMDJiNjdjZWU1NzEzODg0MDNhYTQ0YzQucG5n,type_RlpMYW5UaW5nSGVpU01HQg==,w_19,text_QOeci-WoseS5kOivhOWFq-WNpg==,size_19,x_14,y_14,interval_2,color_FFFFFF,effect_softoutline,shc_000000,blr_2,align_1"}]""",
        '_cover_images_map':f"""[{{"src":"{COVER_IMG}","origin_src":"{COVER_IMG}"}}]""",
        'subtitle': "",
        'bjhtopic_id': "",
        'bjhtopic_info': "",
        'clue': 1,
        'bjhmt': "",
        'order_id': "",
        'image_edit_point': """%5B%7B%22img_type%22%3A%22cover%22%2C%22img_num%22%3A%7B%22template%22%3A0%2C%22font%22%3A0%2C%22filter%22%3A0%2C%22paster%22%3A0%2C%22cut%22%3A0%2C%22any%22%3A0%7D%7D%2C%7B%22img_type%22%3A%22body%22%2C%22img_num%22%3A%7B%22template%22%3A0%2C%22font%22%3A0%2C%22filter%22%3A0%2C%22paster%22%3A0%2C%22cut%22%3A0%2C%22any%22%3A0%7D%7D%5D""",
    }
    # print(formData)
    url= "https://baijiahao.baidu.com/pcui/article/publish?callback=_SAVE_PUBLISH_"  #发布
    # url= "https://baijiahao.baidu.com/pcui/article/save?callback=bjhdraft"  #草稿
    html = wadeTools_Request.wade_Request_post(url=url,addHeader={"Content-Type": "application/x-www-form-urlencoded","Cookie": COOKIE,"token":TOKEN},data=formData)
    # print(html.text)
    # print(html.json())
    return html.json()

def baiduPostContent_Caogao(TITLE,CONTENT,COVER_IMG,COOKIE,TOKEN,ABSTRACT):
    # exit(code=0)
    from urllib import parse

    # exit(0)
    formData = {
        'type': 'news',
        'title': TITLE[0:30],
        'content': CONTENT,
        'abstract': ABSTRACT,
        'len': 27917,
        'activity_list%5B0%5D%5Bid%5D': 408,
        'activity_list%5B0%5D%5Bis_checked%5D': 1,
        'source_reprinted_allow': 0,
        'original_status': 0,
        'original_handler_status': 1,
        'isBeautify': 'false',
        'cover_layout': 'one',
        # 'cover_images': '''[{"src":"https://pic.rmb.bdstatic.com/bjh/news/95950f5a98b8b4346e386ba63f29e650.jpeg?x-bce-process=image/crop,w_719,h_479,x_0,y_16","cropData":{"x":0,"y":16,"width":719,"height":479},"machine_chooseimg":1,"isLegal":0}]''',
        # 'cover_images': f'''[{{"src":"{COVER_IMG}?x-bce-process=image/crop,w_719,h_479,x_0,y_16","cropData":{{"x":0,"y":16,"width":719,"height":479}},"machine_chooseimg":1,"isLegal":0}}]''',
        'cover_images': f'''[{{"src":"{COVER_IMG}","cropData":{{"x":0,"y":16,"width":719,"height":479}},"machine_chooseimg":1,"isLegal":0}}]''',
        # '_cover_images_map':f"""[{"src":"https://pica.zhimg.com/50/v2-f78f790008da504b230ea3c28f8ef62e_720w.jpg?x-bce-process=image/crop,w_719,h_479,x_0,y_16","origin_src":"https://pic.rmb.bdstatic.com/bjh/news/95950f5a98b8b4346e386ba63f29e650.jpeg?x-bce-process=image/watermark,bucket_baidu-rmb-video-cover-1,image_YmpoL25ld3MvNjUzZjZkMjRlMDJiNjdjZWU1NzEzODg0MDNhYTQ0YzQucG5n,type_RlpMYW5UaW5nSGVpU01HQg==,w_19,text_QOeci-WoseS5kOivhOWFq-WNpg==,size_19,x_14,y_14,interval_2,color_FFFFFF,effect_softoutline,shc_000000,blr_2,align_1"}]""",
        # '_cover_images_map':f"""[{{"src":"{COVER_IMG}?x-bce-process=image/crop,w_719,h_479,x_0,y_16","origin_src":"{COVER_IMG}?x-bce-process=image/watermark,bucket_baidu-rmb-video-cover-1,image_YmpoL25ld3MvNjUzZjZkMjRlMDJiNjdjZWU1NzEzODg0MDNhYTQ0YzQucG5n,type_RlpMYW5UaW5nSGVpU01HQg==,w_19,text_QOeci-WoseS5kOivhOWFq-WNpg==,size_19,x_14,y_14,interval_2,color_FFFFFF,effect_softoutline,shc_000000,blr_2,align_1"}}]""",
        '_cover_images_map':f'''[{{"src":"{COVER_IMG}","origin_src":"{COVER_IMG}"}}]''',
        'subtitle': "",
        'bjhtopic_id': "",
        'bjhtopic_info': "",
        'clue': 1,
        'bjhmt': "",
        'order_id': "",
        'image_edit_point': """%5B%7B%22img_type%22%3A%22cover%22%2C%22img_num%22%3A%7B%22template%22%3A0%2C%22font%22%3A0%2C%22filter%22%3A0%2C%22paster%22%3A0%2C%22cut%22%3A0%2C%22any%22%3A0%7D%7D%2C%7B%22img_type%22%3A%22body%22%2C%22img_num%22%3A%7B%22template%22%3A0%2C%22font%22%3A0%2C%22filter%22%3A0%2C%22paster%22%3A0%2C%22cut%22%3A0%2C%22any%22%3A0%7D%7D%5D""",
    }
    # print(formData)
    # url= "https://baijiahao.baidu.com/pcui/article/publish?callback=_SAVE_PUBLISH_"  #发布
    url= "https://baijiahao.baidu.com/pcui/article/save?callback=bjhdraft"  #草稿
    html = wadeTools_Request.wade_Request_post(url=url,addHeader={"Content-Type": "application/x-www-form-urlencoded","Cookie": COOKIE,"token":TOKEN},data=formData)
    # print(html.text)
    # print(html.json())
    print(html.json()['errmsg'])

    return html.json()

if __name__ == '__main__':
    # 全局常量
    COOKIE = 'BIDUPSID=BE8639BCD6607F8E530A42EDF074C840; PSTM=1670469138; BAIDUID=BE8639BCD6607F8E1BE32DEFB23A5C7D:FG=1; BAIDUID_BFESS=BE8639BCD6607F8E1BE32DEFB23A5C7D:FG=1; BA_HECTOR=05248g0k218ha1208k0l2q8f1hp2lgi1h; ZFY=buAudwpR0vBRD6P5ezRDV9LQdhCmtYyBZgNKaXNUn:Bs:C; PSINO=1; delPer=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BCLID=10829574753594179326; BDSFRCVID=ROFOJexroG0rxIcjuJUe5TwNmeKKv7TTDYrECenrWhab4-CVJeC6EG0PtEeydEu-EHtdogKKBeOTHg_F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tR3a3RT_2RjsHJAk-4QEbbQH-UnLqhj93eOZ04n-ah02q4nV-P6hylL8jJOfWtr-W23q_Mbm3UTKsqONhR5RM-_Vj2cmLfT-0bc4KKJxbp5qJJbH5Dcpyb0OhUJiBMj-Ban70M7IXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbRO4-TFhe5oQDMK; BDSFRCVID_BFESS=ROFOJexroG0rxIcjuJUe5TwNmeKKv7TTDYrECenrWhab4-CVJeC6EG0PtEeydEu-EHtdogKKBeOTHg_F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; BCLID_BFESS=10829574753594179326; H_BDCLCKID_SF_BFESS=tR3a3RT_2RjsHJAk-4QEbbQH-UnLqhj93eOZ04n-ah02q4nV-P6hylL8jJOfWtr-W23q_Mbm3UTKsqONhR5RM-_Vj2cmLfT-0bc4KKJxbp5qJJbH5Dcpyb0OhUJiBMj-Ban70M7IXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbRO4-TFhe5oQDMK; PHPSESSID=v5nh9lmql6vif1fjq803stu1l1; RECENT_LOGIN=1; canary=0; gray=1; Hm_lvt_f7b8c775c6c8b6a716a75df506fb72df=1670469313; browserupdateorg=pause; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; H_PS_PSSID=37858_36557_37690_37910_37765_37759_37904_26350_22158_37881; BDUSS_BFESS=Edud3NHbVdRZ2p0M295U2lHZ2xsWmg1cVJ2bFdHdlJvbjlBZmVQUWlsZ1pHN2xqRVFBQUFBJCQAAAAAAAAAAAEAAACQvPM4u6jT0LDZ0fnAogAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABmOkWMZjpFjZ; BDUSS=Edud3NHbVdRZ2p0M295U2lHZ2xsWmg1cVJ2bFdHdlJvbjlBZmVQUWlsZ1pHN2xqRVFBQUFBJCQAAAAAAAAAAAEAAACQvPM4u6jT0LDZ0fnAogAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABmOkWMZjpFjZ; Hm_lpvt_f7b8c775c6c8b6a716a75df506fb72df=1670483779; RT="z=1&dm=baidu.com&si=372c7e8a-5a20-4b61-9c58-4522f1ce78af&ss=lbeiapya&sl=18&tt=2wgg&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; ab_sr=1.0.1_MWEzMmQ5MzdhMmUxMDU5ZTExOTM3MWViNjIxMGI5ODFkOWM3YmZhMWQ2NjFlZmU5NDQyOTdjMjQ3MTM1ZjFhOWQ3MDljZTkwYzVjMjczY2RhNjQ5NzhhZWU3ZTk3YWE0ZjE4OTQ2NmZlZDMwZThiYzVhMzk1ZGZkOTlkMDIxZDRhYmVhOTFmZmRhMGQ5OTQ1YmI3NGI2ZTAxMGJmZjcxOQ==; devStoken=901516d0ad6212f1fbf1a0fcf039a7214364508e0e705efa88a98a7c5faf1257; bjhStoken=1ae176cca6bbb7980847e9932c9524364364508e0e705efa88a98a7c5faf1257'
    TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9iYWlqaWFoYW8uYmFpZHUuY29tIiwiYXVkIjoiaHR0cDpcL1wvYmFpamlhaGFvLmJhaWR1LmNvbSIsImlhdCI6MTY3MDQ4Mzc4NSwibmJmIjoxNjcwNDQwNTkwLCJleHAiOjE2NzA1MjY5OTB9.UTPXv_fiz1cc7ZcSWV4XwZYvJhi4F1rwcOOGBtCp3Lk'
    ABSTRACT = "我是简介"
    PUBLIST_NUM = 0
    TITLE = f"测试内容的时候，一定要善待键盘"
    CONTENT = f"""<tbody data-diagnose-id="e2f77d464f1fe15541239a7b11fad887"><tr class="firstRow" data-diagnose-id="988b2537036a1b1bbd1ea6d8db17a954"><td width="90" style="word-break: break-all" data-diagnose-id="afc3729b74329c22fd335dbcccd2facf">&#8203;<br></td><td width="90" data-diagnose-id="c96905aa0bd9d8dd86005973f35cf12d"><br></td><td width="90" data-diagnose-id="e8c9e47f4fd9b2ce9bceb741a20f4677"><br></td><td width="90" data-diagnose-id="597ca2910f24e7c4d687eff34fb2b475"><br></td></tr><tr data-diagnose-id="8ee869f95815db1e1b1dae5fcac9dd5c"><td width="90" data-diagnose-id="818d94053470ad80e9ed7dc545dda194"><br></td><td width="90" data-diagnose-id="7390ccecd42f0f96c24cf8f027a8e046"><br></td><td width="90" data-diagnose-id="a63afc6e08e6d5f2443c236a7cedf5d6"><br></td><td width="90" data-diagnose-id="b453ea1be0a90b00c930c8125f842804"><br></td></tr><tr data-diagnose-id="0c5475b8ffda97775a293bbd8f95cf67"><td width="90" data-diagnose-id="8c72ff6e89952f57e300e77e8faa6cfa"><br></td><td width="90" data-diagnose-id="2aa58573aa43b64e98c8f4e04fbb53ae"><br></td><td width="90" data-diagnose-id="99f2a61ee6c9ebfe0fe57ed006141b71"><br></td><td width="90" data-diagnose-id="82b7d2629085bb170b52e76def72475e"><br></td></tr></tbody><p>aaaaaaaaaaaaaaaaaaaaaaaaaaaa</p>【商品卡】<p>测试测试测试测</p><p data-bjh-caption-id="cap-62857951" class="bjh-image-container cant-justify" data-bjh-helper-id="1649741270711" data-bjh-caption-text="" data-bjh-caption-length="16"><img src="https://pic.rmb.bdstatic.com/bjh/news/95950f5a98b8b4346e386ba63f29e650.jpeg?x-bce-process=image/watermark,bucket_baidu-rmb-video-cover-1,image_YmpoL25ld3MvNjUzZjZkMjRlMDJiNjdjZWU1NzEzODg0MDNhYTQ0YzQucG5n,type_RlpMYW5UaW5nSGVpU01HQg==,w_19,text_QOeci-WoseS5kOivhOWFq-WNpg==,size_19,x_14,y_14,interval_2,color_FFFFFF,effect_softoutline,shc_000000,blr_2,align_1" data-bjh-origin-src="https://pic.rmb.bdstatic.com/bjh/news/95950f5a98b8b4346e386ba63f29e650.jpeg" data-bjh-type="IMG" data-bjh-params="%7B%22org_url%22%3A%22https%3A%2F%2Fpic.rmb.bdstatic.com%2Fbjh%2Fnews%2F95950f5a98b8b4346e386ba63f29e650.jpeg%22%7D" data-diagnose-id="88ffc2da7feca8d68e5c9ff3586b6604" data-w="719" data-h="540"></p><p><br></p>"""

    # baiduInit(COOKIE=COOKIE)
    # print(PUBLIST_NUM)
    # baiduImageUrl(COOKIE=COOKIE)  #转换图片链接
    SHOP_CARD_WEB_CODE = baidu_selectShopItem(COOKIE=COOKIE,ITEM_ID=100021771660)  #插入商品卡
    # baiduPostContent_Caogao(CONTENT=CONTENT.replace('【商品卡】',SHOP_CARD_WEB_CODE),TITLE=TITLE,COVER_IMG='',COOKIE=COOKIE,TOKEN=TOKEN,ABSTRACT=ABSTRACT)   #发布文字
    # print(SHOP_CARD_WEB_CODE)