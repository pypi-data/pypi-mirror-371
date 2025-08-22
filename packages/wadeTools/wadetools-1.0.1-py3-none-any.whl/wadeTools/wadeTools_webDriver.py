#!/usr/bin/env python
#coding=utf-8
# author:wade
# contact: 317909531@qq.com
# datetime:2021/4/5 22:14
#wo  ai ni

"""
文件说明：
方便直接使用模拟浏览器进行网页操作，ReuseBrowser 类完成了对于已经打开的网页进行操作的功能，再也不用重新启动网页测试了
driver.find_element_by_id(‘id’)
driver.find_element_by_xpath('xpath')
driver.find_element_by_link_text('link_text')
driver.find_element_by_partial_link_text('partial_link_text')
driver.find_element_by_name('name')
driver.find_element_by_tag_name('tag_name')
driver.find_element_by_class_name('class_name')
driver.find_element_by_css_selector('css_selector')
"""

from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Remote
import pickle

class ReuseBrowser(Remote):
    """专门用来保证复用一个浏览器的类，超级好用，2022年8月亲测
        记录一个bug，我在2022年的秋天，我使用了    selenium 的4.4版本，
        我打算同时运行多个程序使用同一个网页，而调试的时候没事，exe的时候就会出现找不到就旧的窗口
        所以，我查了是因为 Exception是：can't set attribute 怎么解决呢？还不能运行的 selenium 版本改成 3.141.0 就可以了 不要最新的

        pip install selenium==3.141.0
        """

    def __init__(self, command_executor, session_id):

        self.r_session_id = session_id
        Remote.__init__(self, command_executor=command_executor, desired_capabilities={})

    def start_session(self, desired_capabilities, browser_profile=None):

        capabilities = {'desiredCapabilities': {}, 'requiredCapabilities': {}}
        for k, v in desired_capabilities.items():
            if k not in ('desiredCapabilities', 'requiredCapabilities'):
                capabilities['desiredCapabilities'][k] = v
            else:
                capabilities[k].update(v)
        if browser_profile:
            capabilities['desiredCapabilities']['firefox_profile'] = browser_profile.encoded

        self.w3c = "specificationLevel" in self.capabilities
        self.capabilities = options.Options().to_capabilities()
        self.session_id = self.r_session_id
        self.w3c = True


def get_wade_driver():
    """打开浏览器，保存浏览器地址 到web.data"""
    try:
        print('准备链接旧窗口')
        with open('web.data','rb') as f:
            webdata = pickle.load(f)
        print("旧窗口：",webdata)
        driver = ReuseBrowser(webdata[0], webdata[1])
        print(driver.window_handles)
        driver.switch_to.window(driver.window_handles[-1])  #切换到最新得页面，保证永远页面永远有效
        # exit()
        # driver = ReuseBrowser("http://127.0.0.1:54885", "47507182d69d578585e80c66d28d35a5")
        print(driver.title)  #利用获取title来判断是否有浏览器程序，也不会打扰到当前页面

    except Exception as e:
        print(e)
        print(f'error file:{e.__traceback__.tb_frame.f_globals["__file__"]}')
        print(f"error line:{e.__traceback__.tb_lineno}")
        print('未检测到窗口，初始化新窗口')
        url = 'https://channels.weixin.qq.com/post/create'
        option = webdriver.ChromeOptions()
        # # option.add_argument('--headless')  # 开启无界面模式
        # # option.add_argument('--disable-gpu')  # 禁用显卡
        option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 禁止js反爬虫
        option.add_argument('--disable-blink-features=AutomationControlled')
        # 配置浏览器类型
        # prefs = {"profile.managed_default_content_settings.images": 2}  #禁止加载图片
        # option.add_experimental_option("prefs", prefs)  #禁止加载图片
        # # 设置cmd窗口不弹出来
        driver = webdriver.Chrome(executable_path='chromedriver', chrome_options=option)

        weblist = [driver.command_executor._url,driver.session_id]
        with open('web.data','wb') as f:
            pickle.dump(weblist,f)
        print('保存浏览器句柄,','创建的新窗口ID为：',weblist ,'已经保存到webdata中')
        # while True:
        #     print(driver.window_handles)
    return driver




# 等待某个元素加载成功
def waitItem(driver,time,className):
    WebDriverWait(driver, time).until(
        EC.presence_of_element_located((By.CLASS_NAME, className)))

def parstCookies2dict(driver):
    """将driver获取得cookie转换为字典格式方便提取"""
    cookie_parse = dict()
    for ck in driver.get_cookies():
        cookie_parse[ck['name']] = ck['value']
    cookie_Dict = cookie_parse
    return cookie_Dict
def parstCookies2str(driver):
    """将cookie转换为字符串  xxx=aaa;bbb=ccc;这种格式可以方便request调用"""
    cookie = driver.get_cookies()
    cookie_parse = dict()
    for ck in cookie:
        cookie_parse[ck['name']] = ck['value']
        # 将字典拼成字符串
    cookies = ''.join([str(k) + '=' + str(v) + ';' for k, v in cookie_parse.items()])
    return cookies
if __name__ == '__main__':
    driver = get_wade_driver()
    driver.get('http://www.tbzhu.com')
    # driver.find_element_by_class_name()



