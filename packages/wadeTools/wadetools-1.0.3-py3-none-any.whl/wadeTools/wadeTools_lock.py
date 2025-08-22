import os
import time
import sys
"""
防止同时使用一个程序的锁
from mutex_lock import SimpleLock
browser_lock = SimpleLock(lock_file="browser_operation.lock")
browser_lock.lock():  # 上锁
browser_lock.unlock()  # 确保释放锁



browser_lock.lock(timeout=30):  # 上锁  timeout也可以不写   最多等待30秒



"""
try:
    # 尝试导入Windows的锁模块
    import msvcrt
except ImportError:
    msvcrt = None
try:
    # 尝试导入Unix的锁模块
    import fcntl
except ImportError:
    fcntl = None


class SimpleLock:
    def __init__(self, lock_file="resource.lock"):
        """初始化锁对象，跨平台支持"""
        self.lock_file = lock_file
        self.file_handle = None

    def lock(self, timeout=None, check_interval=1):
        """上锁操作，支持跨平台

        :param timeout: 超时时间(秒)，None表示无限等待
        :param check_interval: 检查间隔时间(秒)
        :return: 是否成功获取锁
        """
        start_time = time.time()

        while True:
            # 检查是否超时
            if timeout is not None and (time.time() - start_time) > timeout:
                return False

            try:
                # 尝试创建并锁定文件
                self.file_handle = open(self.lock_file, 'w')

                # 根据不同操作系统使用不同的锁机制
                if sys.platform.startswith('win') and msvcrt:
                    # Windows系统
                    msvcrt.locking(self.file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                elif fcntl:
                    # Unix/Linux/Mac系统
                    fcntl.flock(self.file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                else:
                    # 不支持文件锁的系统，使用简单的文件存在性检查
                    print("警告: 系统不支持文件锁，使用基础文件检查模式")

                return True

            except (BlockingIOError, PermissionError, IOError):
                # 锁已被占用，关闭文件句柄
                if self.file_handle:
                    self.file_handle.close()
                    self.file_handle = None
                print("发现被占用")
                # 等待一段时间后重试
                time.sleep(check_interval)
            except Exception as e:
                print(f"上锁失败: {e}")
                if self.file_handle:
                    self.file_handle.close()
                    self.file_handle = None
                return False

    def unlock(self):
        """解锁操作，释放资源"""
        if self.file_handle:
            try:
                # 释放文件锁
                if sys.platform.startswith('win') and msvcrt:
                    # Windows系统解锁
                    msvcrt.locking(self.file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                elif fcntl:
                    # Unix系统解锁
                    fcntl.flock(self.file_handle, fcntl.LOCK_UN)

                self.file_handle.close()
            except Exception as e:
                print(f"解锁失败: {e}")
            finally:
                self.file_handle = None

        # 删除锁文件
        if os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
            except Exception as e:
                print(f"删除锁文件失败: {e}")
