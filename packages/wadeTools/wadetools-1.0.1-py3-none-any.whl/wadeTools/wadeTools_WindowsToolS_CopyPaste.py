import os
import pyperclip
"""
说明：复制和获取剪贴板内容库
说明：基础库
    getQinghuaSource() #导出需求库文件
    installRequirement()  #安装库文件
"""
def copy(text):
    pyperclip.copy(f'{text}')  # 将hello复制到剪贴板，复制的内容可使用ctrl+v粘贴
def paste():
    a = pyperclip.paste()
    return a
def getQinghuaSource():
    os.system("pip install pip -U")
    os.system("pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple")

def getNetRequirement():
    import requests
    rootpath = os.path.join(os.getcwd(),'requirements.txt')
    html = requests.get(url="https://files.shimonote.com/euPiYQToiBJNKBpm.txt?auth_key=1642397602-a6lEr2a5TfE98aE0-0-fa6e71717da7b275d3673f8c98a3cbb3&response-content-disposition=attachment%3B+filename%3D%22requirements.txt%22%3B+filename%2A%3DUTF-8%27%27requirements.txt")
    # 保存
    print(html.text)
    with open(rootpath, 'rb') as f:
        f.write(html.content)
        f.close()
    # rootpath = os.path.join(os.getcwd())
    # os.system(f"cd {rootpath}")
    # os.system("pip freeze > requirements.txt")
def getRequirement():
    rootpath = os.path.join(os.getcwd())
    os.system(f"cd {rootpath}")
    os.system("pip freeze > requirements.txt")
def installRequirement():
    rootpath = os.path.join(os.getcwd())
    os.system(f"cd {rootpath}")
    os.system("pip install -r requirements.txt")
if __name__ == '__main__':
    # copy("nihao")
    # getQinghuaSource()
    installRequirement()

