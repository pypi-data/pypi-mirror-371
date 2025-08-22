# coding: utf-8
#adb控制手机的必备小刀
import os
import time

"""
看到某个关键词就做出指定动作：watchText
死等某个关键词出现后在继续下一步操作 waitText
向手机送文件：addFileToAndroid
删除手机中的文件：delFileFromPhone

开启driver  
--------------------------------------------------------
import uiautomator2 as u2
driver = u2.connect_usb()
--------------------------------------------------------
具体配置看石墨就行
"""

def checkExists(driver,text):
    """
    查询页面上是否存在这个文本
    :param text:
    :return:
    """
    if driver.xpath(f'//*[@text="{text}"]').exists == True:
        return True
    else:return False
def waitText(driver,text):
    """
    （死等）在一定时间内等待文本出现
    :param driver:
    :param text:
    :return:
    """
    while (checkExists(driver, text)==False):  #
        print(f"等待字符....：{text}，出现.......")
        time.sleep(1)


def watchText(driver,text,action):
    """
    看到这个文本就执行某个操作
    :param driver:
    :param text:
    :return:
    d.press("back")  # 点击back键
    d.press("home")  # 点击home键
    d.press("left")  # 点击左键
    d.press("right")  # 点击右键
    d.press("up")  # 点击上键
    d.press("down")  # 点击下键
    d.press("center")  # 点击中间
    d.press("menu")  # 点击menu按键,菜单键
    d.press("search")  # 点击搜索按键
    d.press("enter")  # 点击enter键，键盘上的Enter键
    d.press("delete")  # 点击删除按键，delete（or del)对应键盘上的DEL键 用于删除）
    d.press("recent")  # 点击近期活动按键,(recent apps)
    d.press("volume_up")  # 音量+
    d.press("volume_down")  # 音量-
    d.press("volume_mute")  # 静音
    d.press("camera")  # 相机拍照按钮
    d.press("power")  # 电源键

    """
    while (checkExists(driver, text)==True):  #
        print(f"观察到：{text}，执行动作：{action}")
        driver.press(f"{action}")
        time.sleep(2)




def addFileToAndroid(driver,fileName,filepath,android_directory_name):
    """
    将windows下的文件推到模拟器文件夹里，输入保存得文件名和哪个文件夹目录下
    :param fileName: windos中选择的文件名
    :param filepath: windos中选择的文件的绝对路径
    :param directory_name: 目标文件夹：Movies就是放到movies文件夹，dicm就是放在dicm文件夹里  android_directory_name = 'Movies'
    :return:
    """
    driver.push(os.path.join(filepath,fileName), f"/sdcard/{android_directory_name}/")  #推送文件到movie文件夹，savepath="/sdcard/Movies/"
    #一定要广播
    driver.shell(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///storage/emulated/0/{android_directory_name}/{fileName}')
    time.sleep(1)

def delFileFromPhone(driver,fileName,android_directory_name):
    """
    删除模拟器文件夹里文件删除，文件名和哪个文件夹目录下
    :param fileName:
    :param directory_name:Movies就是放到movies文件夹，dicm就是放在dicm文件夹里
    :return:
    """
    driver.shell(f'rm /sdcard/{android_directory_name}/{fileName}')  # 删除文件
    #一定要广播，安卓里边需要这个内容，不用懂
    driver.shell(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///storage/emulated/0/{android_directory_name}/{fileName}')
    time.sleep(1)
