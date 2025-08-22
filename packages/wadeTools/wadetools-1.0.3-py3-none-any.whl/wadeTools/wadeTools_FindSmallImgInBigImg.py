# -*- encoding=utf-8 -*-
import os
import time
import wadeTools_ErZhiHua
import wadeTools_DuiBiJPG
import cv2
import wadeTools_ScreenShot
'''
by：shenhuawade
qq: 317909531
功能：负责比对两幅图的相似度，越接近0越相似，越接近1，越差异

find_picture()
------------------------------------------
输入参数target: 待搜素的大图
输入参数template: 搜素的小图，尺寸必须小于target
-------------------------------------------
输出参数min_val: 越接近0越相似，越接近1越偏离，0.005以下基本可以认为是准确的
输出参数x: 匹配左上角的位置，用于定位
输出参数y: 匹配左上角的位置，用于定位
------------------------------------------
code/time:2019.12.29
'''

"""
matchTemplate():
参数image:待搜索的图像(大图)
参数temple:搜索模板,需要和原图一样的数据类型且尺寸不能大于源图像
参数result:比较结果的映射图像,其必须为单通道,32位浮点型图像,如果原图(待搜索图像)尺寸为W*H,而temple尺寸为w*h,则result尺寸一定是
    (W-w+1)*(H-h+1)
参数method:指定匹配方法,有如下几种:
    CV_TM_SQDIFF:平方差匹配法
    CV_TM_SQDIFF_NORMED:归一化平方差匹配法
    CV_TM_CCORR:相关匹配法
    CV_TM_CCORR_NORMED:归一化相关匹配法
    CV_TM_CCOEFF:系数匹配法
    CV_TM_CCOEFF_NORMED:化相关系数匹配法
"""
"""
minMaxLoc()函数
作用:一维数组当作向量,寻找矩阵中最小值和最大值位置
"""

def find_picture(target,template):
    # #二值化处理
    target= wadeTools_ErZhiHua.custom_threshold(target)
    template= wadeTools_ErZhiHua.custom_threshold(template)

    #获得模板图片的高宽尺寸
    theight, twidth = template.shape[:2]

    '''相似度对比'''
    #执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result1 = cv2.matchTemplate(target,template,cv2.TM_SQDIFF_NORMED)    #趋近于0
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(result1)
    # cv2.normalize(result1, result1, 0, 1, cv2.NORM_MINMAX, -1)
    '''汉明距离对比'''
    cropped = target[min_loc1[1]:min_loc1[1] + theight, min_loc1[0]:min_loc1[0] + twidth]  # 裁剪坐标为[y0:y1, x0:x1]
    cv2.imencode('.png', cropped)[1].tofile(os.path.join('shotImgLOG', f"{int(round(time.time() * 1000))}找到的图.png"))
    cv2.imencode('.png', template)[1].tofile(os.path.join('shotImgLOG', f"{int(round(time.time() * 1000))}myimage模版图.png"))
    # cv2.imwrite(os.path.join('shotImgLOG', f"{int(round(time.time() * 1000))}__zhao.png"), cropped)
    # cv2.imwrite(os.path.join('shotImgLOG', f"{int(round(time.time() * 1000))}__myimage模版图.png"), template)
    # 利用pil 的格式进行汉明距离测试
    # 先把template的numpy格式转为pil的img
    from PIL import Image
    # similary 越接近1说明两张图相符
    similary = wadeTools_DuiBiJPG.phash_img_similarity(Image.fromarray(template), Image.fromarray(cropped))


        # 真正的找到了
    targetCopy = target  #在副本上画线框，不污染原图，后边还需要在原图上截取图片做汉明距离比对，所以不能污染原图
    cv2.rectangle(targetCopy, min_loc1, (min_loc1[0] + twidth, min_loc1[1] + theight), (0, 0, 225), 2)
    # cv2.namedWindow("RGBimg--ShowasGBRimg", cv2.WINDOW_NORMAL)
    # cv2.imshow(f"RGBimg--ShowasGBRimg", target)
    imgname = f"{int(round(time.time() * 1000))}自定义找图范围.png"
    # cv2.imwrite(os.path.join('shotImgLOG',imgname),targetCopy)
    cv2.imencode('.png', targetCopy)[1].tofile(os.path.join('shotImgLOG',imgname))


    # cv2.namedWindow("RGBimg--ShowasGBRimg2", cv2.WINDOW_NORMAL)
    # cv2.imshow(f"RGBimg--ShowasGBRimg2", targetCopy)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    #拿到了最佳点之后，通过xy就可以截取到这个屏幕图片的局部
    #对大图片裁切，对比他们的特征码，如果明汉距离通过，说明是真的对比成功



    x = min_loc1[0]
    y = min_loc1[1]
    # 矩形框的长和宽
    return min_val1, x, y, similary, twidth, theight



if __name__ == '__main__':
    # wadeTools_ScreenShot.screenShot()
    # target = cv2.imread('c.png')[:, :, ::-1]   #因为cv2.imread读取的是gbr通道，需要反转成rgb格式
    # template = cv2.imread('t.png')[:, :, ::-1]
    # print(type(target))
    # # 通道反转img[:, :, ::-1]
    #
    # #不做灰度对比效果
    # min_val1, x, y, similary, twidth, theight = find_picture(target,template)
    # print(min_val1,similary)


    # 做灰度对比效果
    target = cv2.imread('8.png')[:, :, ::-1]  # 因为cv2.imread读取的是gbr通道，需要反转成rgb格式
    template = cv2.imread('8.png')[:, :, ::-1]
    # cv2.namedWindow('input_image')  # 设置为WINDOW_NORMAL可以任意缩放
    # cv2.imshow('input_image', target)
    target_ErZhi_numpy = wadeTools_ErZhiHua.custom_threshold(target)  # 获取目标图片的灰度二值化图片
    cv2.namedWindow("target_ErZhi_numpy", cv2.WINDOW_NORMAL)
    cv2.imshow("target_ErZhi_numpy", target_ErZhi_numpy)
    # wadeTools_ErZhiHua.local_threshold(target)
    # wadeTools_ErZhiHua.custom_threshold(target)
    template_ErZhi_numpy = wadeTools_ErZhiHua.custom_threshold(template)  # 获取模板中图片的灰度二值化图片
    cv2.namedWindow("template_ErZhi_numpy", cv2.WINDOW_NORMAL)
    cv2.imshow("template_ErZhi_numpy", template_ErZhi_numpy)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(type(target))
    # 通道反转img[:, :, ::-1]

    # # 不做灰度对比效果
    # min_val1, x, y, similary, twidth, theight = find_picture(target_ErZhi_numpy, template_ErZhi_numpy)
    # print(min_val1)
    # print(similary)




    '''AttributeError: 'NoneType' object has no attribute 'shape
        报错是因为图片路径问题
    '''