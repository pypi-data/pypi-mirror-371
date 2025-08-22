# wadeTools



1.调用方法：
import sys
sys.path.append('C:/wadeTools/')
//加入系统库
import wadeTools_webDriver
driver = wadeTools_webDriver.get_wade_driver()



2021年修改引入方式，第一种调用会出现找不到库文件，不方面

2.调用方法，进入wadeTools文件夹，有个setup.py文件 可以把需要发布的库文件放进去
然后点击安装.bat就可以进行本地使用


linux安装
切换到wadeTools目录下，运行,不带sudo会提示无权限
sudo python3 setup.py install

