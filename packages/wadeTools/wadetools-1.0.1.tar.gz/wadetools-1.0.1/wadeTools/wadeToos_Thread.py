""" 需要固定数量的线程时候，用简单的方法来最直观 import time, threading
    lock = threading.Lock()  #感觉资源会冲突加个锁
    with lock:
        pass

"""
from concurrent.futures import as_completed

""" 有大量相同任务需要并行的话，采用线程池concurrent.futures模块来比较省事 from concurrent.futures import ThreadPoolExecutor"""
import time,threading
from wadeTools import wadeTools_Police
from concurrent import futures
import tkinter
def a(name):
    time.sleep(2)
    print(f"睡了{name}秒")
    return threading.current_thread().name,threading.active_count()
def b(name):
    timess =5
    time.sleep(timess)
    print(f"睡了{timess}秒")
    return 5

@wadeTools_Police.cost_time
def threadExample():
    thread_obj1 = threading.Thread(target=a,name="hellow",args=("name",))
    thread_obj2 = threading.Thread(target=b,name="nihao",args=("name",))
    thread_obj1.start()
    thread_obj2.start()
    thread_obj1.join()  # 让主进程等你呦
    thread_obj2.join()
    print(thread_obj1.name)
    print(thread_obj1.is_alive())

def ThreadPoolExample():
    # 功能同上executor.submit()遍历
    with futures.ThreadPoolExecutor(max_workers=5) as pool:
        taskList =[]
        task1 = pool.submit(a,int(time.time()*1000))
        task2 = pool.submit(a,int(time.time()*1000))
        taskList.append(task1)
        taskList.append(task2)

    for future in futures.as_completed(taskList):
        result = future.result()
        print("线程%s拿到的返回值%s" % (threading.current_thread().name, result))
    pool.shutdown()
    print(task1.running())




if __name__ == '__main__':
    threadExample()

    # # 我想 实现一个状态监控窗口，里边有控制单元
    # # 输入名字、按钮变量、功能函数、运行时候可以随时控制
    # window = tkinter.Tk()
    # def func():
    #     print('我被触发了')
    # def refresh_data():
    #     print(123)
    #     window.after(1, refresh_data)



    # window.after(100, refresh_data)  # 这里的100单位为毫秒
    # window.mainloop()