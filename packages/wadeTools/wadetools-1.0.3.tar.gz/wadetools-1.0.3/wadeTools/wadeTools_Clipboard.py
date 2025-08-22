# -- coding: utf-8 --
# 作者:shenhuawade
"""说明文档：
20241208复制到剪切板
"""
from win32clipboard import OpenClipboard, CloseClipboard, EmptyClipboard, SetClipboardData, RegisterClipboardFormat
import ctypes
def insertClicpboard(insertHtml):
    """
    复制到剪切板主函数
    :param insertHtml:
    :return:
    """
    # insertHtml = "<p>123</p>"  # 待插入的文本
    # 写入数据
    template = f"""Version:0.9
    StartHTML:0000000001
    EndHTML:0000000000
    StartFragment:0000000000
    EndFragment:0000000000
    <html>
    <body>
    <!--StartFragment-->{insertHtml}</br><!--EndFragment-->
    </body>
    </html>"""
    # 定义要申请的内存大小
    size = 10000 + len(template)

    # 使用 ctypes.create_string_buffer()函数来申请内存空间
    buffer = ctypes.create_string_buffer(size)

    buffer.raw = f"{template}".encode('utf-8')
    # 读取数据
    # data = buffer.raw
    # # 打印数据
    # print(data)
    OpenClipboard()
    EmptyClipboard()
    cfid = RegisterClipboardFormat("HTML Format")
    SetClipboardData(cfid, buffer.raw)
    CloseClipboard()

if __name__ == '__main__':
    html = '''<p><img src="http://img30.360buyimg.com/shaidan/s720x540_jfs/t1/136628/3/14287/1924070/5f9d8058Ee25048a4/937e211cf8b0bf97.jpg" alt=""></p><ul><li>宝妈群里都在推荐好奇的皇家铂金御裤果断中草下单收到货真的非常满意颜值非常高包装很精美龙纹非常吸晶尿裤很柔软手感舒适保护宝宝嫩嫩的pp而且尿裤很薄内含3D透氧层一晚上没换宝宝的pp都没有红吸量也不错也没有漏尿的情况出现超级赞！</li></ul><hr><h2 style="font-size: 1.2em;line-height: 1.5;font-weight: 600;">二、<span>【文章标题】</span>用户关心的问题</h2><div><ol><li>问题：这款会红屁屁吗<p>♥好奇皇家御裤很透气的，正常来说是不会红屁屁的，但是也得勤换洗，不然再透气的纸尿裤也会红屁屁。</p></li><li>问题：宝妈们，这款的NB码柔软吗，是薄款的吗，预产期7月份。<p>♥好奇皇家御裤裸感芯0.2cm，挺轻薄透气的，七月份天气很热，挺适合的。</p></li><li>问题：会不会觉得有点硬<p>♥不硬啊，特别软</p></li><li>问题：皇家铂金和大王天使哪个好用？谢谢<p>♥没用过大王的，一直都是用的好奇皇家御裤，挺轻薄透气的，孩子用了也没红屁屁等问题。</p></li><li>问题：请问现在宝宝还有10天出月子现在8斤8两，出月子想用纸尿裤，现在囤货买多大合适？<p>♥再用几片NB码，可以开始囤S码了，但别囤太多</p></li><li>问题：皇家御裤和小桃裤哪个更薄更好用？<p>♥小桃裤比较薄，但因为冬天我选择了皇家</p></li><li>问题：84片够用多久？<p>♥半个月左右</p></li><li>问题：容易红屁股吗？<p>♥我崽不会红，挺柔软的</p></li><li>问题：皇家铂金装有味道吗<p>♥有味呢！腰那里味道很大</p></li><li>问题：是不是容易侧漏啊<p>♥我家的用了这么久没有一片侧漏，放心买吧</p></li></ol></div><hr><h2 style="font-size: 1.2em;line-height: 1.5;font-weight: 600;">三、<span>【文章标题】</span>配置参数、类型</h2><hr><p><img src="http://img30.360buyimg.com/shaidan/s720x540_jfs/t1/118437/14/14760/63573/5f365302E10f8570a/8742e0f8212b5826.jpg" alt=""></p><hr><h2 style="font-size: 1.2em;line-height: 1.5;font-weight: 600;">四'''
    insertClicpboard(html)

    # insertClicpboard("""<p>nihao</p><img src="https://p6-flow-imagex-sign.byteimg.com/ocean-cloud-tos/FileBizType.BIZ_BOT_ICON/3251350_1697011106512121056.png~tplv-a9rns2rl98-icon-tiny.png?rk3s=9956f44f&x-expires=1714738220&x-signature=wR9a%2F0Q%2BNCr2i0bBiJ535ZEJ0zc%3D" alt="图片描述" />""")