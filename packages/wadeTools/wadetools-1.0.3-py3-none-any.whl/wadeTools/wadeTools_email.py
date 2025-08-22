import yagmail
import wadeTools.wadeTools_log
my_logger = wadeTools.wadeTools_log.MyLogger.create_logger()
def sendEmail(email,title,content):
    """
    发送邮件的函数，使用jiuyinwadevip@163.com来进行操作.
    :param email:邮件地址
    :param title:标题
    :param content:内容
    :return: 无返回
    """
    try:
        # 链接邮箱服务器
        yag = yagmail.SMTP(user="jiuyinwadevip@163.com", password="test123456789", host='smtp.163.com')
        # 邮箱正文
        contents = [f'{content}']
        # 发送邮件
        yag.send(f'{email}', f'{title}', contents)

    except Exception as e:
        my_logger.debug(e)
        pass

if __name__ == '__main__':
    # sendEmail('317909531@qq.com','这是来自我的一封信','我很好，我是内容')
    my_logger.setLevel('DEBUG')
    my_logger.debug("nif12adf")