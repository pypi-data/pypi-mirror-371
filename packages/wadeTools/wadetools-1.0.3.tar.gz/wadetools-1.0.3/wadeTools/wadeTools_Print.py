# -*- encoding=utf-8 -*-

# 打印的升级版
import sys
def wadePrint(msg,*args):
    print(f'\033[0;36m{msg}',*args, '\033[0m   \033[0;37m ',sys._getframe(1).f_code.co_filename, sys._getframe(1).f_lineno,'\033[0m')
def wadeBluePrint(msg,*args):
    print(f'\033[0;36m{msg}',*args, '\033[0m   \033[0;37m ','\033[0m')
def wadeRedPrint(msg,*args):
    print(f'\033[0;31m{msg}',*args, '\033[0m   \033[0;37m ',sys._getframe(1).f_code.co_filename, sys._getframe(1).f_lineno,'\033[0m')

if __name__ == '__main__':
    wadeRedPrint(1,3,4)
    wadeBluePrint(1,3,4)
