# -*- encoding=utf-8 -*-
"""
轮寻,txt 增加内容，读取内容
txt文件对象 = wadeTxtObject(filename='111.txt')
txt文件对象.deleteItem("")
"""
import random
import re
from wadeTools.wadeTools_log import my_logger
class wadeTxtObject:
    """
    txt扩展类支持读取 OBJ.data   增加：OBJ.addxxxx  删除OBJ。delxxxxx
    """
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.__load()
    def getTextList(self):
        """获取文本的内容"""
        self.deleteBlankLines()
        return self.data

    def lunxunTxt(self):
        """
        随机返回文本的一行：返回值为str类型
        :param filepath: 传入文件相对路径或者绝对路径：./1.txt  c:/1.txt
        :return:列表
        """
        return str(random.choice(self.data))
    def additem_to_Txt(self, text):
        # 续写txt，不存在则自动创建
        if type(text) != str:  # 判断是否是是字符串，不是的话，强制改为字符串
            text = str(text)
        self.data.append(text)
        self.save()

    def addList_to_TXT(self, list):
        # 重新保存txt，不存在则自动创建
            for i in list:
                if type(i) != str:  # 判断是否是是字符串，不是的话，强制改为字符串
                    i = str(i)
                self.additem_to_Txt(i)
    def deleteItem(self, text):
        if text in self.data:
            self.data.remove(text)
            self.save()
        else:
            my_logger.warning("列表删除查无该数据")
    def deleteBlankLines(self):
        """
        删除所有的空行
        :return:None
        """
        self.data = list(filter(None, self.data))
        self.save()

    def findWord(self, Word):
        """
        列出txt中包含某个内容的列表
        :param findWord:  包含的内容
        :return: 返回列表
        """
        matchList = []
        for i in self.data:
            if Word in i:
                matchList.append(i)
        return matchList

    def getListByText_form_Sign(self, lineWord):
        """
        按照约定格式取内容，用于取得账号信息
        print(OBJ.getListByText_form_Sign("你好@----@你好发@----@发发@----@发的"))
        解释：'@----@' 是我们要分割的标记       lineWord 输入字符串 "你好@----@你好发@----@发发@----@发的"
        返回['你好', '你好发', '发发', '发的']
        """

        resultList = re.split('@----@', lineWord)
        # 输出结果
        try:  # 去除空字符
            resultList.remove("")
        except:
            pass
        return resultList

    def clear(self):
        self.data.clear()  # 清空self.data列表
        self.save()  # 保存清空后的内容到文件

    def __load(self):  # 内部函数
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.data = [line.strip() for line in file]  # 读取每一行并删除前后的空白字符
        except FileNotFoundError:
            self.save()
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.data = [line.strip() for line in file]  # 读取每一行并删除前后的空白字符

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            for line in self.data:
                file.write(line + '\n')  # 在每条文本后添加换行符
        self.__load()



if __name__ == '__main__':


    TXT111 = wadeTxtObject(filename='111.txt')

    print(TXT111.getListByText_form_Sign("你好@----@你好发@----@发发@----@发的.html"))



