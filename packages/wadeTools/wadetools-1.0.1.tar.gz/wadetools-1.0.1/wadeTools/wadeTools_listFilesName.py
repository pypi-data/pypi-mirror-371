# cython: language_level=3
# #获取目录下面的文件
import os
from wadeTools import wadeTools_log
from wadeTools.wadeTools_Print import wadePrint
my_logger = wadeTools_log.my_logger
'''
功能：
os.getcwd()  获取当前目录路径
os.listdir(path) 列出当前目录下文件列表
os.remove(path)  删除文件
os.rename(src,dst)  重命名

单个项目功能：列举目录下的文件内容,读取文件内所有img内容和txt内容，生成图片文件名地址列表和txtlist表，存txt位置地址

geImgAndTextFile()  内置的文件夹是textContent
getImgAndTextFile()  内置的文件夹是docxContent

------------------------------------------
#读取文件列表
wadePrint(wadeTools_listFilesName.list_files_relativePath('movie'))  #读取文件列表)
wadePrint(wadeTools_listFilesName.list_files_fullPath('movie'))  #读取文件列表)
------------------------------------------
code/time:2019.1.5
'''
import os
import shutil


def empty_folder(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            shutil.rmtree(dir_path)
    os.rmdir(folder_path)
    os.makedirs(folder_path)
def getMovieFile():
    names = os.listdir('Movies')  # type list
    if len(names)>0:  #存在文件

        path = os.getcwd()
        filename = names[0]
        fromDir = os.path.join(path, 'Movies')
        fileFromDIR = os.path.join(fromDir, filename)

        return filename, fileFromDIR
    else:
        wadePrint(f"Movies文件夹里边没有素材了，请及时添加素材")
        return False

def getImgAndTextFile():
    names = os.listdir('textContent')  # type list
    if len(names)>0:  #存在文件

        path = os.getcwd()
        filename = names[0]  #文件夹1，文件夹2
        fromDir = os.path.join(path, 'textContent')
        fileFromDIR = os.path.join(fromDir, filename) #C:\xiaohuohua\AAAVIP工具箱\VIPtool\textContent\1
        # wadePrint(filename)
        # wadePrint(fileFromDIR)
        erziNames = os.listdir(fileFromDIR)  #进入子目录，拿到内容

        textDir = ''        #文档路径
        textname =''        #文档名字
        imgNametexts =''     #图片名字，为了打开图片
        imgFileDirList = []  #图片路径
        if len(erziNames)>0:  #1里面存在内容

            for erziFile in erziNames:
                wadePrint(erziFile)
                if erziFile.endswith(('jpg','png','jpeg')):
                    imgName = str(erziFile)
                    imgFileDir = os.path.join(fileFromDIR, erziFile)
                    wadePrint(imgFileDir)
                    imgFileDirList.append(imgFileDir)

                    imgNametexts = imgNametexts+"\""+imgFileDir +"\""+ ' ' # 图片列表
                    # wadePrint(erziFile)
                if erziFile.endswith('.txt'):      #txt文档
                    # wadePrint(erziFile)
                    textname = erziFile.split('.txt')[0]
                    wadePrint(textname)
                    textDir =os.path.join(fileFromDIR, erziFile)
                    # 如果是照片，就进行测试，如果有返回正确内容就，记录到json里边

            #图片名，图片路径，多长图片名拼接，图片地址列表
        return textname,textDir,imgNametexts,imgFileDirList,fileFromDIR
    else:
        wadePrint(f"textContent文件夹里边没有图文素材了，请及时添加素材")
        return False

def getDocxFile():  #获取word文档
    names = os.listdir('docxContent')  # type list
    if len(names)>0:  #存在文件

        path = os.getcwd()
        filename = names[0]  #文件夹1，文件夹2
        fromDir = os.path.join(path, 'docxContent')
        fileFromDIR = os.path.join(fromDir, filename) #C:\xiaohuohua\AAAVIP工具箱\VIPtool\textContent\1
        # wadePrint(filename)
        # wadePrint(fileFromDIR)
        erziNames = os.listdir(fileFromDIR)  #进入子目录，拿到内容

        textDir = ''        #文档路径
        textname =''        #文档名字
        imgNametexts =''     #图片名字，为了打开图片
        imgFileDirList = []  #图片路径
        if len(erziNames)>0:  #1里面存在内容

            for erziFile in erziNames:
                wadePrint(erziFile)
                if erziFile.endswith('.docx'):      #txt文档
                    # wadePrint(erziFile)
                    textname = erziFile.split('.docx')[0]
                    wadePrint(textname)
                    textDir =os.path.join(fileFromDIR, erziFile)
                    # 如果是照片，就进行测试，如果有返回正确内容就，记录到json里边

            #图片名，图片路径，多长图片名拼接，图片地址列表
        return textname,textDir,fileFromDIR
    else:
        wadePrint(f"textContent文件夹里边没有图文素材了，请及时添加素材")
        return False


def list_files_relativePath_ByFile(dirname,File='mp4'):
    """
    列出目标路径下的所有 文件的名 不包括目录
    :param dirname: 目标路径，可以是相对，也可以是绝对
    :return:
    """
    try:
        if not os.path.exists(f'{dirname}'):
            my_logger.debug(f'{dirname}，这个路径不存在')
            return []
        names = os.listdir(f'{dirname}')
        if len(names)==0:

            wadePrint(f"{dirname}文件夹里边没有素材了，请及时添加素材")
            # try:
            #     import PySimpleGUI as sg
            # except:
            #     os.system("pip install PySimpleGui")  # 调用cmd命令 安装PY库
            #     import PySimpleGUI as sg
            wadePrint(f"{dirname}文件夹里边没有素材了，请及时添加素材")
            # exit()
            return []
        fileList = []  # 目标路径里边的文件
        dirList = []  # 目标路径下的目录
        for num, i in enumerate(names):
            if i.endswith(File):
                # wadePrint(i)
                names[num] = os.path.join(os.path.abspath(f'{dirname}'), i)
                if not os.path.isfile(names[num]):
                    dirList.append(i)
                else:
                    fileList.append(i)
        del names
        return fileList

    except Exception as e:
        my_logger.debug(f"{dirname}没有找到，请新建")
        return []
def list_files_relativePath(dirname):
    """
    列出目标路径下的所有 文件的名 不包括目录
    :param dirname: 目标路径，可以是相对，也可以是绝对
    :return:
    """
    try:
        if not os.path.exists(f'{dirname}'):
            my_logger.debug(f'{dirname}，这个路径不存在')
            return []
        names = os.listdir(f'{dirname}')
        if len(names)==0:

            wadePrint(f"{dirname}文件夹里边没有素材了，请及时添加素材")
            # try:
            #     import PySimpleGUI as sg
            # except:
            #     os.system("pip install PySimpleGui")  # 调用cmd命令 安装PY库
            #     import PySimpleGUI as sg
            wadePrint(f"{dirname}文件夹里边没有素材了，请及时添加素材")
            # exit()
            return []
        fileList = []  # 目标路径里边的文件
        dirList = []  # 目标路径下的目录
        for num, i in enumerate(names):
            # wadePrint(i)
            names[num] = os.path.join(os.path.abspath(f'{dirname}'), i)
            if not os.path.isfile(names[num]):
                dirList.append(i)
            else:
                fileList.append(i)
        del names
        return fileList

    except Exception as e:
        my_logger.debug(f"{dirname}没有找到，请新建")
        return []
def list_files_fullPath(dirname):
    """
    输入一个文件夹，看看里边有没有文件，没有的话就提醒,有的话就列出所有文件的绝对路径,目录的话自动过滤掉
    :param dirname:目标路径
    :return: 路径下的文件
    """
    try:
        if not os.path.exists(f'{dirname}'):
            my_logger.debug(f'{dirname}，这个路径不存在')
            return []
        fromDir = os.getcwd()

        # wadePrint(fromDir)
        names = os.listdir(f'{dirname}')
        # wadePrint(os.path.abspath(f'{filename}'))
        # wadePrint(names)
        if len(names)==0:
            my_logger.debug(f"{dirname}文件夹里边没有素材了，请及时添加素材")
            # try:
            #     import PySimpleGUI as sg
            # except:
            #     os.system("pip install PySimpleGui")  #调用cmd命令 安装PY库
            #     import PySimpleGUI as sg
            wadePrint(f"{dirname}文件夹里边没有素材了，请及时添加素材")
            # exit()
            return []
        else:
            fileList = []  #目标路径里边的文件
            dirList =[]    #目标路径下的目录
            for num,i in enumerate(names):
                # wadePrint(i)
                names[num] = os.path.join(os.path.abspath(f'{dirname}'),i)
                if not os.path.isfile(names[num]):
                    dirList.append(names[num])
                else:
                    fileList.append(names[num])
            del names
            return fileList

    except Exception as e:
        my_logger.debug(e)
        my_logger.debug(f"{dirname}没有找到，请新建")
        return []


if __name__ == '__main__':
    wadePrint(list_files_fullPath('D:/'))
    # filename ='textContent'
    # # filelist = list_files(filename)
    # if getImgAndTextFile():  #如果有内容
    #     textname,textDir, imgNametexts,imgFileDirList,fileFromDIR =getImgAndTextFile()
    #     wadePrint('111')
    #     wadePrint(imgFileDirList[0])
    #     wadePrint(len(imgFileDirList))
    #
    #     # FindMain_PC.rm_file(FatherDir, False)  #删除
    # filename ='docxContent'
    # # filelist = list_files(filename)
    # if getDocxFile():  #如果有内容
    #     docxname,docxDir,fileFromDIR =getDocxFile()
    #     wadePrint(docxname)
    #     wadePrint(docxDir)
    #     wadePrint(fileFromDIR)





