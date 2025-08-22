"""
保存日志文档：
saveLog()
显示实时日志
showLOG(msg,self.text类型)

#保存listBox对象内容
saveListbox(ListBox对象)

#加载listBox对象内容
readListbox(ListBox对象)
"""
import pickle
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from wadeTools import wadeTools_ReadAndWrite, wadeTools_encodingTxt, wadeTools_readConfig_ini, wadeTools_TkinterClass
from tkinter import filedialog
from tkinter import ttk
import re
import traceback

class WadeApplication():
    def __init__(self):

        self.initData = wadeTools_readConfig_ini.ReadConfig('config.ini')
        self.window = tk.Tk()
        self.window.geometry()
        self.log_line_num = 0
        self.window.grid()
        self.create_widgets()
        self.window.mainloop()

    def create_widgets(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.menubar = tk.Menu(self.window)
        # 创建一个下拉菜单“文件”，然后将它添加到顶级菜单中
        self.filemenu = tk.Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="打开", command=self.openFile)
        self.filemenu.add_command(label="作者", command=lambda: self.message_showinfo())  # 如果没有lambda:  那么传参模式打开窗口就会调用
        self.menubar.add_cascade(label="文件", menu=self.filemenu)  # 将filemenu加入到顶级菜单menubar
        # 显示菜单
        self.window.config(menu=self.menubar)
        # 软件标志
        self.lable_title = tk.Label(self.window, text="欢迎使用高级协议VIP")
        self.lable_title.grid(row=0, column=0, pady=2)

        # 完整的软件列表内容
        self.canvas1 = tk.Canvas(self.window, relief=tk.FLAT, background="#D2D2D2")
        self.canvas1.grid(row=1, column=0, sticky=tk.EW)
        # 滚动条,先渲染列表，然后 把滚动条覆盖在右侧，联动列表内容
        self.listBox1 = tk.Listbox(self.canvas1)
        self.listBox1.grid(row=1, column=1)
        self.scrool_Bar1 = tk.Scrollbar(self.canvas1)
        self.scrool_Bar1.grid(row=1, column=2, sticky=tk.N + tk.S + tk.E)  # N+S上下伸展 E靠右放置  E+W左右伸展  S靠下放置
        self.scrool_Bar1.configure(command=self.listBox1.yview)
        self.listBox1.configure(yscrollcommand=self.scrool_Bar1.set)

        self.button1 = ttk.Button(self.canvas1, text="开始", command=self.startNOW)
        self.button1.grid(row=7, column=1, sticky=tk.W)
        self.button1 = ttk.Button(self.canvas1, text="删除第一条", command=self.delListBoxFirstOne)
        self.button1.grid(row=7, column=1, sticky=tk.E)
        self.readListbox(self.listBox1)

        self.listBox2 = tk.Listbox(self.window)
        self.listBox2.grid()
        self.readListbox(self.listBox2)
        self.button2 = tk.Button(self.window, text="开始2", command=self.startNOW1)
        self.button2.grid()

        # 左日志文本框
        self.logText = tk.Text(self.window, width=130, height=9)  # 日志框
        self.logText.grid()

    def readWord(self, path):  # 根据路径读取内容
        sec_user_id_List = wadeTools_encodingTxt.readText(path, 'UTF-8')
        return sec_user_id_List

    def openFile(self):  # 打开文件，获取路径
        # 选择文件  返回文件路径
        self.filePath = filedialog.askopenfilename(title="打开文件~~只能是txt文本哦",
                                                   filetypes=(("txt files", "*.txt"),))  # 只能选择单个文件
        fileContentList = self.readWord(self.filePath)
        for num, i in enumerate(fileContentList, start=1):
            self.listBox1.insert(tk.END, f"{i}", )  # END表示最后一个位置插入
        return

    def saveLog(self, msg):
        wadeTools_ReadAndWrite.saveLog(msg)

    def readLog(self):  # return list
        return wadeTools_ReadAndWrite.readLog()

    # 保存列表内容，给一个列表对象，就能实时保存列表内容和读取，直接加载到列表中
    def saveListbox(self, listBox_OBJ):

        stack = traceback.extract_stack()
        filename, lineno, function_name, code = stack[-2]
        vars_name = re.compile(r'\((.*?)\).*$').search(code).groups()[0]
        listBox_OBJ_Name = vars_name.replace('self.', '')

        # print(sys._getframe().f_back.f_locals[listBox_OBJ])
        # print(list(dict(listBox_OBJ=listBox_OBJ).keys())[0])  #获取属性自己的变量名称

        # 构造存储字典：
        # 总字典
        try:
            dataDict = wadeTools_ReadAndWrite.wadeRead('obj.data', 'rb')
        except:
            dataDict = {}
        dataDict[listBox_OBJ_Name] = listBox_OBJ.get(first=0, last=tk.END)
        with open("obj.data", "wb") as fout:
            pickle.dump(dataDict, fout)
        fout.close()
        del dataDict

    def readListbox(self, listBox_OBJ):
        try:

            stack = traceback.extract_stack()
            filename, lineno, function_name, code = stack[-2]
            vars_name = re.compile(r'\((.*?)\).*$').search(code).groups()[0]
            listBox_OBJ_Name = vars_name.replace('self.', '')
            dataDict = wadeTools_ReadAndWrite.wadeRead('obj.data', 'rb')

            listBox_OBJ_List = dataDict[listBox_OBJ_Name]
            for num, i in enumerate(listBox_OBJ_List, start=1):
                listBox_OBJ.insert(tk.END, f"{i}", )  # END表示最后一个位置插入
            del dataDict
        except:
            print("缺少obj.data文件")
        return

    def delListBoxFirstOne(self):  # 删除第一条

        self.saveListbox(self.listBox1)
        self.listBox1.delete(0)

    def startNOW(self):

        self.listBox1.insert(tk.END, self.log_line_num)
        self.showLOG('111', self.logText)

    def startNOW1(self):
        self.listBox2.insert(tk.END, 222)
        self.saveListbox(self.listBox2)
        self.showLOG('111', self.logText)

    def changeColor(self, color="red"):
        # print(self.listbox1.get(first=0, last=tk.END))

        self.listbox1.itemconfig(0, bg=color)  # 标注颜色
        return

    # 运行日志处理函数
    def showLOG(self, logmsg, textOBJ):
        logmsg_in = f"{wadeTools_ReadAndWrite.get_current_time()}:{logmsg}\n"  # 换行
        if self.log_line_num <= 7:
            textOBJ.insert(tk.END, logmsg_in)
            self.log_line_num = self.log_line_num + 1
        else:
            textOBJ.delete(1.0, 2.0)
            textOBJ.insert(tk.END, logmsg_in)

    # 提醒模组
    def message_showinfo(self, title="秘境", msg="我是一个风尘少年，归隐于无形"):
        # 弹出消息,result返回true或者false
        # result = tkinter.messagebox.showinfo(title='秘境', message='我是一个风尘少年，归隐于无形')
        result = tk.messagebox.showinfo(title=title, message=msg)

    def message_askokcancel(self, title="秘境", msg="我是一个风尘少年，归隐于无形"):
        # 弹出对话框,result返回true或者false
        result = tk.messagebox.askokcancel(title=title, message=msg)

    def message_askquestion(self, title="秘境", msg="我是一个风尘少年，归隐于无形"):
        # 弹出对话框,result返回true或者false
        result = tk.messagebox.askquestion(title=title, message=msg)

    def message_askyesno(self, title="秘境", msg="我是一个风尘少年，归隐于无形"):
        # 弹出对话框,result返回true或者false
        result = tk.messagebox.askyesno(title=title, message=msg)

    def message_showerror(self, title="秘境", msg="我是一个风尘少年，归隐于无形"):
        # 弹出对话框,result返回true或者false
        result = tk.messagebox.showerror(title=title, message=msg)

    # 关闭模组：
    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.window.destroy()

class mywin(wadeTools_TkinterClass.WadeApplication):
    #写布局
    def create_widgets(self):
        """
        这里写布局，self.windows是根窗口
        :return:
        """
        return

    def method(self):
        """
        这里写方法，着是方法1，对应窗口内容
        :return:
        """
        return
    #写方法，不用管其他的了

if __name__ == '__main__':
    mywin = WadeApplication()





