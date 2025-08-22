import re

from chardet.universaldetector import UniversalDetector

'''by：shenhuawade
qq: 317909531
功能：自动判断txt的编码格式，都自动转换成utf8编码

readtextMain(filename)
------------------------------------------
输入参数filename: 文件名 '游记：皮尔森啤酒博物馆.txt'
-------------------------------------------
输出参数list: 每行文字组成的列表

------------------------------------------
code/time:2019.1.5
'''


def readText(file,encode_info):
    # 2.按行读取
    textlist =[]
    mylen = 0
    for line in open(file, errors='ignore',encoding=encode_info):
        # 清洗空格后如果不为空就下一步处理
        if line.strip() != '':
            # print(f"本行内容为{line}")
            # 每行的数据都需要清洗空格后进行下一步处理
            abc = line.strip()
            mylen = mylen+len(abc)

            if mylen <= 9900:
                textlist.append(abc)
            else:
                break
        else:
            # print("本行为空")
            pass
    print(mylen)
    return textlist




def get_encode_info(file):
    with open(file, 'rb') as f:
        detector = UniversalDetector()

        for line in f.readlines():
            # print(line)
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        # print(detector.result['encoding'])
        if detector.result['encoding'] == None:
            return 'ascii'
        return detector.result['encoding']


def read_file(file):
    with open(file, 'rb') as f:
        return f.read()


def write_file(content, file):
    with open(file, 'wb') as f:
        f.write(content)


def convert_encode2utf8(file, original_encode, des_encode):
    file_content = read_file(file)
    print(file_content)
    file_decode = file_content.decode(original_encode, 'ignore')
    file_encode = file_decode.encode(des_encode)
    write_file(file_encode, file)



#核心函数
def readtextMain(filename):
    filename = rf'{filename}'
    file_content = read_file(filename)
    encode_info = get_encode_info(filename)
    if encode_info != 'utf-8':
        convert_encode2utf8(filename, encode_info, 'utf-8')
    encode_info = get_encode_info(filename)
    print(encode_info)
    textlist = readText(filename, encode_info)
    return textlist

def paragraph_To_LimiteWordNUM_List(paragraph,limitNum):
    # paragraph = """etc全称Electronic Toll Collection，意思是全自动电子收费系统，是国际上正在努力开发并推广的一种用于公路、大桥和隧道的电子自动收费系统，是智能交通系统的服务功能之一。
    # etc采用车辆自动识别技术完成车辆与收费站之间的无线数据通讯，进行车辆自动感应识别和相关收费数据的交换，运用计算机网络进行收费数据的处理，不停车、不设收费窗口，实现自动收费。
    # etc收费系统每车收费耗时不到两秒，其收费通道的通行能力是人工收费通道的5至10倍。此外，etc还可以使公路收费走向无纸化、无现金化管理，从根本上杜绝收费票款的流失现象，解决公路收费中的财务管理混乱问题；另外，实施etc还能够节约基建费用和管理费用。
    # """
    # result_list = re.split(r'[。\s]', paragraph)  按句号和空格分开
    result_list = re.split(r'[。]', paragraph)   #按句号分隔
    # print(result_list)

    for index,item in enumerate(result_list):
        result_list[index] = item.strip()
    result_list = [i+"。" for i in result_list if i != '']
    print(result_list)
    return result_list

if __name__ == "__main__":

    # filename = r'C:\xiaohuohua\AAAVIP工具箱\VIPtool\疯狂动物城：A movie about growth an.txt'
    # textlist = readtextMain(filename)
    # print(textlist)
    paragraph = """etc全称为Electronic Toll Collection ，是电子不停车收费系统，也就是在高速公路或桥梁上对装了ETC车载器的车辆进行自动收费。
电子不停车收费系统通过安装在车辆挡风玻璃上的车载电子标签与在收费站 etc 车道上的微波天线之间进行的专用短程通讯，利用计算机联网技术与银行进行后台结算处理，从而达到车辆通过高速公路或桥梁收费站无需停车而能交纳高速公路或桥梁费用的目的。
    """
    paragraph_To_LimiteWordNUM_List(paragraph,limitNum=300)













