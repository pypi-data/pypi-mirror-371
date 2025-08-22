"""图片功能库cv2是传统的BGR模式，pil的image是rgb模式  CV2和PIL读取图像方法与区别对比https://www.cnblogs.com/qdulixing/p/16146861.html"""
import cv2
# 读取图片
import numpy as np

from wadeTools import wadeTools_log

my_logger = wadeTools_log.my_logger

import base64
import requests

def image_url_to_base64(image_url):
    response = requests.get(image_url)
    image_content = response.content
    return base64.b64encode(image_content).decode('utf-8')



def wadeImageRead(image_path):
    """
    利用cv2读取图片，通道默认为BGR,获取np矩阵
    :param image_path:图片的路径，绝对和相对的中英文都行
    :return: <class 'numpy.ndarray'>
    """
    img = cv2.imdecode(np.fromfile(f"{image_path}", dtype=np.uint8), -1)  # 这个可以接纳中文路径

    # img = cv2.imread("C:/Users/wade/Desktop/1.png",cv2.IMREAD_COLOR)  # 默认以BGR形式打开 ,不支持中文，不用了
    return img


# 多个图片拼接同时展示
def wadeImageShowList(imgs, size, layout,sideWidth=4):
    #创建高度的白边
    whiteside_h = np.ones((size[0], sideWidth, 3), dtype='uint8') * 100  #4是4个像素，3是三个维度
    # whiteside_h = np.array(np.random.choice(55,(size[0], sideWidth, 3)),dtype=np.uint8)  #4是4个像素，3是三个维度
    #创建宽度的白边,因为上边宽度增加了
    whiteside_w = np.ones((sideWidth, size[1]+sideWidth, 3), dtype='uint8') * 100  #4是4个像素，3是三个维度
    # whiteside_w = np.array(np.random.choice(55,(sideWidth, size[1]+sideWidth, 3)),dtype=np.uint8)  #4是4个像素，3是三个维度


    imgh =None
    null_img = None
    imgw = None
    """
    多个图片拼接展示,imgs为需要展示的图片数组
    size为展示时每张图片resize的大小
    layout为展示图片的布局例如（3，3）代表3行3列）
    :param imgs: np的图片数组
    :param size: 每张小图的分辨率 元组
    :param layout: 几行几列 （3,2） 3行2列
    :return: np的图片一张
    """
    w = layout[0]
    h = layout[1]
    x = imgs[0].shape[2]  #获取通道数
    if w * h - len(imgs) > 0:
        null_img = np.zeros((size[0]+sideWidth, size[1]+sideWidth, x), dtype='uint8')
        # 注意这里的dtype需要声明为'uint8'，否则和图片矩阵拼接时会导致图片的矩阵失真
        null_img = null_img * 255
    # null_img用来填充当图片数量不足时，布局上缺少的部分
    for i in range(len(imgs)):
        # 和同学交流的过程中发现如果出现有的图片通道不足的时候，会出现合并问题
        # 思考了一下，使用下面这段代码将灰度图片等通道数不足的图片补充成3个通道就ok
        if len(imgs[i].shape) < 3:
            imgs[i] = np.expand_dims(imgs[i], axis=2)
            imgs[i] = np.concatenate((imgs[i], imgs[i], imgs[i]), axis=-1)
        imgs[i] = cv2.resize(imgs[i], size)

        #图片右边和下边加间隔条
        aaa = np.hstack((imgs[i], whiteside_h))  # 水平方向堆叠
        imgs[i] = np.vstack((aaa, whiteside_w))  # 垂直方向堆叠
    for j in range(h):
        for k in range(w):
            if j * w + k > len(imgs) - 1:
                f = k
                while f < w:
                    if f == 0:
                        imgw = null_img
                    else:
                        imgw = np.hstack((imgw, null_img))
                    f = f + 1
                break
            if k == 0:
                imgw = imgs[j * w]
            else:
                imgw = np.hstack((imgw, imgs[j * w + k]))
            print(j * w + k)
        if j == 0:
            imgh = imgw
        else:
            imgh = np.vstack((imgh, imgw))
    return imgh


# 高宽功能：
def wadeImageGetWidth_height(numpy_image):
    """
    :param numpy_image:
    :return:图片宽高
    """
    height = numpy_image.shape[0]  # 高度（行数）
    width = numpy_image.shape[1]  # 宽度（列数）
    my_logger.debug(f"宽:{width}像素,高:{height}像素")
    return width, height


def wadeImageCut(numpy_image, x, y, width, height):
    """
    裁剪图片高度,按照矩形尺寸来切割
     x: 左上角距离左边距离    -(0,0)-(1,0)-(2,0)--------(x,0)-
     y: 左上角距离顶部距离    -(0,1)-(1,1)-(2,1)--------(x,1)
     width: 矩形的宽度       -(0,2)-(x,y)-(2,2)--------(x+width,2)
     height: 矩形的高度      -(0,3)-(x,y+height)-(2,3)--------(x+width,y+height)

    :param numpy_image: np类型的图片
    :param x: 起始点x坐标
    :param y: 起始点y坐标
    :param width: 需要切割矩阵的宽度
    :param height:需要切割矩阵的高度
    :return: np图片
    """
    endX = x + width
    endY = y + height  # 因为截取的坐标可能会超出图片，所以进行最大化修正
    img_w, img_h = wadeImageGetWidth_height(numpy_image)
    if x > img_w or y > img_h:
        my_logger.info("裁切的起始点出现问题，已经重置为x=0，y=0")
        x, y = 0, 0
    if x + width > img_w:
        my_logger.info("裁切的矩形超出图片宽度，x+width已调整为图片最大宽度")
        endX = img_w
    if y + height > img_h:
        my_logger.info("裁切的矩形超出图片宽度，y+height已调整为图片最大宽度")
        endY = img_h

    imgCut = numpy_image[y:endY, x:endX]
    return imgCut


# 通道功能：
def wadeImage_BGR_to_RGB(numpy_image_BGR):
    """
    BGR和RGB的通道转换
    :param numpy_image_BGR:cv2读取的BGR通道图片
    :return: 转换的RGB通道图片
    """
    my_logger.debug(f"BGR和RGB的通道转换")
    numpy_image_RGB = numpy_image_BGR[:, :, ::-1]
    return numpy_image_RGB


def wadeImageGet_B_G_R(numpy_image_BGR):
    my_logger.debug(f"分别获取图片的B、G、R通道")
    B = numpy_image_BGR[:, :, 0]
    G = numpy_image_BGR[:, :, 1]
    R = numpy_image_BGR[:, :, 2]
    return B, G, R


# 显示功能
def wadeImageShow(numpy_image, waitTime=0):
    """
    显示图片,等待时间默认为为永久,waitTime 1000是1秒
    :param numpy_image: cv2读取的图片（np）
    :return: NULL
    """
    cv2.imshow(f'123.jpg', numpy_image)
    cv2.waitKey(waitTime)


if __name__ == '__main__':





    """分割展示四幅图方法"""
    evaJPG = wadeImageRead('333.jpg')
    wadeImageGetWidth_height(evaJPG)
    img_w, img_h = wadeImageGetWidth_height(evaJPG)
    left_img = wadeImageCut(evaJPG, x=0, y=0, width=img_w // 2, height=img_h // 2)
    right_img = wadeImageCut(evaJPG, x=img_w // 2, y=0, width=img_w // 2, height=img_h // 2)
    down_right = wadeImageCut(evaJPG, x=0, y=img_h // 2, width=img_w // 2, height=img_h // 2)
    down_lefg = wadeImageCut(evaJPG, x=img_w // 2, y=img_h // 2, width=img_w // 2, height=img_h // 2)
    resultImg1 = wadeImageShowList([left_img, right_img, down_right,down_lefg ], (600,600), (2,2),sideWidth=0)
    resultImg2 = wadeImageShowList([left_img, right_img, down_right,down_lefg ], (600, 600), (2,2),sideWidth=200)
    resultImg3 = wadeImageShowList([left_img, right_img, down_right,down_lefg ], (600, 600), (2,2),sideWidth=100)
    resultImg4 = wadeImageShowList([left_img, right_img, down_right,down_lefg ], (600, 600), (2,2),sideWidth=10)
    resultImg5 = wadeImageShowList([left_img, right_img, down_right,down_lefg ], (600, 600), (2,2),sideWidth=20)
    cv2.imwrite('1.png',resultImg1)
    cv2.imwrite('2.png',resultImg2)
    cv2.imwrite('3.png',resultImg3)
    cv2.imwrite('4.png',resultImg4)
    cv2.imwrite('5.png',wadeImage_BGR_to_RGB(resultImg4))

    # finallyImg = wadeImageShowList([resultImg1,resultImg2,resultImg3,resultImg4],(600, 600), (1,4))
    # wadeImageShow(cv2.flip(finallyImg,1))

#
# #保存图片
# cv2.imwrite('123.png',img)
#
# #打印图片大小
# print(img.shape)
#
# #获取高宽
# height = img.shape[0]
# width = img.shape[1]
#
# #裁剪 ,顺序是
# """  a: 左上角距离顶部
#      b: 左下角距离顶部
#      c: 左上角距离左边距离
#      d: 右上角距离左边距离"""
# cut_img = img[0: height, 119: width-119]
# cv2.imwrite('1231.png',cut_img)
#
# ##cv2转base64
# import cv2
#
#
# def cv2_base64(image):
#     base64_str = cv2.imencode('.jpg', image)[1].tostring()
#     base64_str = base64.b64encode(base64_str)
#     return base64_str
#
#
# ##base64转cv2
# import base64
# import numpy as np
# import cv2
#
#
# def base64_cv2(base64_str):
#     imgString = base64.b64decode(base64_str)
#     nparr = np.fromstring(imgString, np.uint8)
#     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     return image
