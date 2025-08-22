# 运行警局，负责程序运行
import time
from wadeTools.wadeTools_log import my_logger
import traceback
from os import execl
from sys import exit,executable,argv
from time import sleep

# import winsound

#播放警报
# def playNoticeSong():
    # winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
# 重启任务
def restartProgram():
    for i in range(10):
        sleep(1)
        # winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
    print('程序重启...')
    # 获取当前解释器路径
    p = executable
    # 启动新程序(解释器路径, 当前程序)
    execl(p, p, *argv)
    # 关闭当前程序
    exit()
# 统计任务耗时
def cost_time(func):
    """ 统计函数耗时时间"""
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'函数 {func.__name__} 运行耗时:{time.perf_counter() - t:.8f} s')
        return result
    return fun

# 安全模式（出错了任务接着干）
def safe_Mode(*saveResult):
    """自治系统模式，出错只记录，不停下来出错先重试几次，重试次数满了后报错，由excep内部解决，由logging记录出错问题,返回的是元组"""
    def my_decorator(func):
        def wrapper(*args, **kwargs):
          try:
            # 执行被装饰的函数
            result = func(*args, **kwargs)
          except Exception as e:
            # 记录异常问题

            print(e, traceback.format_exc())
            my_logger.debug(e)
            my_logger.debug(traceback.format_exc())
            my_logger.debug("__________________________________________________________________")
            # 系统出错后返回 预设结果，不影响流程
            return saveResult
          else:
            # 返回装饰后的函数结果
            return result

        return wrapper
    #返回装饰器
    return my_decorator

# 出错报错模式开启
def unsafe_Mode():
    """依赖系统模式，出错记录后，停下来抛出错误给主线，出错先重试几次，重试次数满了后抛出错误，由logging记录出错问题"""
    def my_decorator(func):
        def wrapper(*args, **kwargs):
          try:
            # 执行被装饰的函数
            result = func(*args, **kwargs)
          except Exception as e:
            # 记录异常问题
            my_logger.debug(e)
            my_logger.debug(traceback.format_exc())
            my_logger.debug("__________________________________________________________________")
            raise Exception
          else:
            # 返回装饰后的函数结果
            return result

        return wrapper
    #返回装饰器
    return my_decorator




if __name__ == '__main__':
    @safe_Mode([1],[2])
    def task1():
        print(1+"3") #故意报错
    try:  # 这个是主程序设计的方式
      for i in range(5):
          print(task1())
    except:
      print(888888)
