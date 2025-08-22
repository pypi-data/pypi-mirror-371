# coding:utf-8
# 单例模式
"""可以解决全局变量的难题，保证在线程之间的通信，实现信息表的统一管理"""

import threading
import time
# from wadeTools import wadeTools_log

class Singletion(object):

    '''外部存储的是类成员变量，实例化中__dict__不会保存这类内容
    用它来持久化：pickle不能序列化的变量
    '''
    instance  = None
    __init__flag = False
    lock = threading.RLock()
    windows={}
    # my_logger = wadeTools_log.MyLogger.create_logger()
    def __init__(self):
        if not Singletion.__init__flag:
            # print('init执行了')
            self.name = '全局变量'
            self._global_dict = {}  # 保存全局变量,不要直接赋值获取，用set get来获取不会报错
            self._gol_ui_dict = {}  # 保存全局UI变量,不要直接赋值获取，用set get来获取不会报错
            Singletion.__init__flag = True

    def __new__(cls, *args, **kwargs):
        # 返回空对象，init中的跨文件不能用
        # 返回空对象
        with cls.lock:
            if cls.instance is None:
                cls.instance = super().__new__(cls)
            return cls.instance


    def gol_save_value(self, key, value):
        self._global_dict[key] = value  # 定义一个全局变量

    def gol_get_value(self, key):
        try:
            return self._global_dict[key]  # 获得一个全局变量，不存在则提示读取对应变量失败
        except:
            print('全局字典中没有：' + key + '键值\r\n')

    def gol_print_value(self):
        print(self._global_dict)

    def gol_clear_value(self):
        self._global_dict = {}

    def ui_save_Value(self, key, value):  # 保存UI中变量的方法
        self._gol_ui_dict[key] = value

    def ui_get_Value(self, key):  # 获得一个全局变量，不存在则提示读取对应变量失败
        try:
            return self._gol_ui_dict[key]
        except:
            print('全局UI字典中没有：' + key + '键值\r\n')

    def ui_print_value(self):
        print(self._gol_ui_dict)

    def ui_clear_value(self):
        self._global_dict = {}


if __name__ == '__main__':

    gol = Singletion


    # gol.printgol()

    def work1():
        from wadeTools import acd
        #
        acd.works()
        # works()
        # print(gol)
        # num = 1
        # while True:
        #     num = num + 1
        #     gol.gol_save_value('aaa', num)
        #     time.sleep(3)
        #     print(333)
        #     print(gol.__dict__)
    def work2():
        gol = Singletion()
        print(gol)



    s1 = threading.Thread(target=work1)
    s2 = threading.Thread(target=work2)
    # s1.setDaemon(True)
    # s2.setDaemon(True)
    s1.start()
    s2.start()

    # gol.printgol()

    print(gol)
    time.sleep(2)

