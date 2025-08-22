import time

import wmi
from wadeTools import wadeTools_Print
import ctypes

def is_locked():
    ''' 用法
        from wadeTools import wadeTools_getSystemInfo
        while wadeTools_getSystemInfo.is_locked(): #如果锁屏的话就是True
        wadePrint("电脑锁屏，暂停工作，等待10秒后重试.....")
        time.sleep(10)
    '''
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    return hwnd == 0  # 锁屏时返回True

def get_mac_address():
    try:
        c = wmi.WMI()
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            return interface.MACAddress
    except:
        return "获取MAC地址失败"

def get_system_manufacturer():
    try:
        c = wmi.WMI()
        system_info = c.Win32_ComputerSystem()[0]
        return system_info.Manufacturer
    except:
        return "获取系统制造商信息失败"

def get_system_model():
    try:
        c = wmi.WMI()
        system_info = c.Win32_ComputerSystem()[0]
        return system_info.Model
    except:
        return "获取系统型号失败"

def get_operating_system():
    try:
        c = wmi.WMI()
        os_info = c.Win32_OperatingSystem()[0]
        return os_info.Caption
    except:
        return "获取操作系统信息失败"

if __name__ == "__main__":
    # mac_address = get_mac_address()
    # system_manufacturer = get_system_manufacturer()
    # system_model = get_system_model()
    # operating_system = get_operating_system()
    # wadeTools_Print.wadeBluePrint("狮子庙中学统计软件正版化统计：以下是你系统信息，选中后右键可以复制:\n")
    # print("MAC地址:", mac_address)
    # print("计算机品牌:", f"{system_manufacturer} {system_model}")
    # print("操作系统:", operating_system)
    # input("按回车键退出程序...")
    while True:
        print(is_locked())
        time.sleep(1)