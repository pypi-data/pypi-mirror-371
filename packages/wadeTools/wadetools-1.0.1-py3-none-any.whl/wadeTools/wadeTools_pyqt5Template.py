# # coding:utf-8
"""pyqt懒省事 的写信号，写连接 ，写槽函数都想懒省事，填入需要懒省事的ui名称，剩下的就复制粘贴"""

def makeInputEidtCode(uiEditCodeList):
    print('--------------------------------------------------------------------------------------------\n')
    for item in uiEditCodeList:
        print(f"signal_{item} = pyqtSignal(str)  # {item}输入框")

    print('--------------------------------------------------------------------------------------------\n')

    for item in uiEditCodeList:
        print(f"my_signal.signal_{item}.connect(self.solt_{item}) # {item}绑定槽")

    print('--------------------------------------------------------------------------------------------\n')

    for item in uiEditCodeList:
        print(f"""
        # {item}槽函数
        def solt_{item}(self, _:str):
            self.ui.{item}.setText(_)""")

    print('--------------------------------------------------------------------------------------------\n')

def makeBtnCode(uiBtnCodeList):
    print('--------------------------------------------------------------------------------------------\n')
    for item in uiBtnCodeList:
        print(f"self.ui.{item}.clicked.connect(self.handle_{item}) # 按钮{item}绑定槽")

    print('--------------------------------------------------------------------------------------------\n')

    for item in uiBtnCodeList:
        print(f"""
    # {item}按钮响应handle函数
    def handle_{item}(self, _:str):
        def innerFunc():
            pass
        task = Thread(target=innerFunc)
        task.start()""")
    print('--------------------------------------------------------------------------------------------\n')


if __name__ == '__main__':
    uiList = [
        "ui_postMaxNum_edit",
              ]
    uiBtnList = [
        'ui_loginBaiduAccount_btn',
        'ui_startPostTask_btn',
                 ]
    makeInputEidtCode(uiList)
    # makeBtnCode(uiBtnList)