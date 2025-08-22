class Error_info(Exception):

    #提醒，不影响主程序
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
class Error_break(Exception):

    #停止程序
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
class Error_continue(Exception):
    #跳过循环
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Error_notAdd(Exception):
    #跳过循环
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)