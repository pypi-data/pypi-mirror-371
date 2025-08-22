#!/usr/bin/env python
# coding=utf-8
'''自动创建文件目录'''
from wadeTools.wadeTools_Print import wadePrint

'''文件移动'''
import os
import shutil


def checkFilePath(relativePath, filename=None):
    path = os.getcwd()
    path = os.path.join(path, relativePath)
    if not os.path.exists(path):
        os.makedirs(path)
    if filename:
        with open(os.path.join(os.getcwd(), path, filename), 'w+', encoding='utf-8') as f:
            f.write("")


import os
import shutil


def remove_file(filename, old_dir, new_dir):
    """
    注释： 实现将一个文件从一个文件夹 移动到另一个目标文件夹，old_dir, new_dir都采用的是相对路径
    :param filename:  需要移动的文件名
    :param old_dir:   旧文件夹（相对路径）
    :param new_dir:   需要移动到新文件夹（相对路径）
    :return:
    """
    try:
        checkFilePath(relativePath=old_dir)
        checkFilePath(relativePath=new_dir)
        file_path = old_dir + '/' + filename
        target_path = os.path.join(new_dir, filename)
        if os.path.exists(target_path):
            # 直接删除目标路径下已存在的同名文件
            os.remove(target_path)
        shutil.copy2(file_path, new_dir)
        os.remove(file_path)
    except Exception as e:
        wadePrint(e)
        pass


if __name__ == '__main__':
    # checkFilePath(relativePath='./saveFile/')
    # checkFilePath(relativePath='./成品/')
    # remove_file(filename='1.py',old_dir=r"./saveFile/", new_dir=r"./成品/")

    print(os.path.abspath('.'))
    print(os.getcwd())
    print(os.path.abspath('./saveFile'))
    print(os.path.abspath('./成品'))
    print(os.path.abspath('../README.md'))
