import winreg
import ctypes
# import PySimpleGUI as sg
# 设置系统代理，取消系统代理
# 打开注册表键
import requests

INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
    r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
    0, winreg.KEY_ALL_ACCESS)

# 设置刷新
INTERNET_OPTION_REFRESH = 37
INTERNET_OPTION_SETTINGS_CHANGED = 39
internet_set_option = ctypes.windll.Wininet.InternetSetOptionW

def set_key(name, value):
    # 修改键值
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)
    winreg.SetValueEx(INTERNET_SETTINGS, name, 0, reg_type, value)

def open_proxy(proxy_server):
    # 启用代理
    set_key('ProxyEnable', 1) # 启用
    set_key('ProxyServer', proxy_server) # 设置代理服务器
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)

def closed_proxy():
    # 禁用系统的代理
    set_key('ProxyEnable', 0) # 禁用
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
# 启用代理并设置代理服务器为 'http://proxy.example.com:8080'
# enable_proxy('http://proxy.example.com:8080')

def changeAgent():
    # 设置系统代理
    global proxies
    url = 'https://proxy.qg.net/allocate?Key=9XFOUQ5B&Num=1&AreaId=&DataFormat=txt&DataSeparator=%5Cr%5Cn&Detail=0'
    html = requests.get(url,timeout=10)
    print('切换新代理：',html.text)

    key = '9XFOUQ5B'
    passwd = '2F5079EA8A6B'
    proxy = f'http://{key}:{passwd}@{html.text}'
    proxy = html.text

    # proxies = {
    #     "http": proxy,
    #     "https": proxy
    # }
    return proxy
def changeAgentButton(): #  切换系统代理按钮


    sg.theme('DarkAmber')  # 设置当前主题色
    # 界面布局，将会按照列表顺序从上往下依次排列，二级列表中，从左往右依此排列
    layout = [[sg.B("切换代理", key="切换代理"),sg.B("关闭代理", key="关闭代理"),sg.I("状态",key="Status")]
              ,[sg.B("查看当前地址", key="查看当前地址"),sg.T("地区状态",key="地区状态")]]

    def my_long_operation():
        print("点击按钮")
        closed_proxy() # 关闭代理
        newAgent = changeAgent()
        windows['Status'].update(f"系统代理:{newAgent}")
        open_proxy(newAgent)  # 开启代理

    def getAddressNow():  # 打开查看ip地址
        html = requests.get("http://myip.ipip.net/")
        print(html.text)
        windows['地区状态'].update(f"区域:{html.text}")

    # 创造窗口
    windows = sg.Window('代理窗口', layout, location=(0, 0), font=("宋体", 10))

    while True:
        event, values = windows.Read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            print('代理窗口关闭')
            break
        if event == '切换代理':  # 登录按钮
            windows.perform_long_operation(my_long_operation, '-finish-')
        if event == '查看当前地址':  # 登录按钮
            windows.perform_long_operation(getAddressNow, '-finish-')
        if event == '关闭代理':  # 登录按钮
            windows['Status'].update(f"系统代理已关闭")
            windows.perform_long_operation(closed_proxy(), '-finish-')
            windows['地区状态'].update(f"区域:当前本机区域")
    windows.close()

def startAgentThread():
    # 多进程，因为tk不支持在多线程中开启
    from concurrent.futures import ProcessPoolExecutor
    executor = ProcessPoolExecutor(max_workers=5)
    executor.submit(changeAgentButton)
    # executor.shutdown(wait=False)
    # with ProcessPoolExecutor(max_workers=5) as executor:
    #     executor.submit(changeAgentButton)




    # import threading
    # task1 = threading.Thread(target=changeAgentButton)
    # task1.start()
if __name__ == '__main__':
    # changeAgentButton() # 是窗口函数
    startAgentThread()  # 是在进程里开启一个窗口函数
    # changeAgentButton()  # 是窗口函数
    # getAddressNow()
    # disable_proxy() # 关闭代理
    # print(changeAgent())
    # enable_proxy(changeAgent())  # 开启代理
