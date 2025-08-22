"""
日志模块，我在2022年8月思考我只有两种需求，做软件时，将print用my_logger.debug()代替
例：
from wadeTools import wadeTools_log
my_logger = wadeTools_log.my_logger

    my_logger = MyLogger.create_logger   #初始化,由于是单例模式，整个默认不用初始化了
    my_logger.debug(输出详细信息)         #打印
    my_logger.info("输出关键信息信息）     #打印
    mylogger.setlevel("DEBUG")   #调试模式
    mylogger.setlevel("INFO")    #运行模式

"""

import logging
import threading
from logging.handlers import TimedRotatingFileHandler
import time

'''

默认日志等级划分

DEBUG    等级最低的，最详细的日志信息，典型应用场景是 问题诊断
INFO     信息详细程度仅次于DEBUG，通常只记录关键节点信息，用于确认一切都是按照我们预期的那样进行工作
WARNING  当某些不期望的事情发生时记录的信息（如，磁盘可用空间较低），但是此时应用程序还是正常运行的
ERROR    由于一个更严重的问题导致某些功能不能正常运行时记录的信息
CRITICAL 当发生严重错误，导致应用程序不能继续运行时记录的信息

'''



class MyLogger():
    """才用了单例模式，保证日志记录器整个项目中只能有一个"""
    instance = None
    __init__flag = False
    lock = threading.RLock()
    def __init__(self):
        if not MyLogger.__init__flag:  #如果没有实例化过，就运行一次，如果实例化过了，这里的代码就不会运行了
            # print('init执行了')
            MyLogger.__init__flag = True
            self.my_logger = MyLogger.create_logger()
    def __new__(cls, *args, **kwargs):
        # 返回空对象，init中的跨文件不能用
        # 返回空对象
        with cls.lock:
            if cls.instance is None:
                cls.instance = super().__new__(cls)
            return cls.instance
    @staticmethod  # 静态方法,使用时可用类/实例调用,只在名义上归类管理
    def create_logger():

        # 获取日志收集器,并设置名称为my_logger(若不设置名字,则为默认日志收集器root)
        my_logger = logging.getLogger("my_logger")
        my_logger.setLevel("DEBUG")  # 收集等级默认为DEBUG

        # 创建一个输出到控制台的处理器
        control_hander = logging.StreamHandler()
        control_hander.setLevel("WARNING")  # 设置输出到控制台的处理器的输出等级为ERROR
        my_logger.addHandler(control_hander)  # 添加处理器并绑定在日志收集器上   ,addHandler:增加处理器, removeHandler:删除处理器

        # 用文件记录日志，记录级别为DEBUG
        filename = time.strftime("%Y%m%d") + ".txt"
        import os
        path = os.getcwd()
        path = path + "/运行日志"
        if not os.path.exists(path):
            os.makedirs(path)

        if not os.path.exists(filename):
            with open(os.path.join(os.getcwd(), path, filename), 'a+', encoding='utf-8') as f:
                # f.write("日志记录")
                pass # 新建文件
        file_handler = TimedRotatingFileHandler(filename=os.path.join(os.getcwd(), path, filename), when='D',
                                                interval=1, encoding='utf-8')
        file_handler.setLevel("DEBUG")  # 设置输出到文件的处理器的输出等级为DEBUG
        my_logger.addHandler(file_handler)

        # 设置输出到文件与控制台的格式
        formatter = logging.Formatter('%(filename)s-->line:%(lineno)d    %(levelname)s   %(asctime)s\n%(message)s\n')
        file_handler.setFormatter(formatter)
        control_hander.setFormatter(formatter)
        return my_logger
my_logger = MyLogger().my_logger # 默认初始化可直接采用类调用
# a = 100
#
# # # assert a==0
# # my= MyLogger() #可创建实例调用

# my_logger.debug(my_logger)
# my_logger.debug("in3fo")
# my_logger.info("info")
# my_logger.setLevel('INFO')
# my_logger.debug(a)
# my_logger.debug("in3fo")
# my_logger.info("info")
# # my_logger.warning("warn")
# # my_logger.error("error")
# # my_logger.critical("critical")
