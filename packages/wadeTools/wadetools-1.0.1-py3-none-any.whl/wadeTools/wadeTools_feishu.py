"""
使用方法：
send_feishu_message()  可以独立调用
👇是调用方法


send_feishu_message(message_content="你好，我是旺财")

"""

from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Alignment, NamedStyle, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
# 导入外部工具类（保持原引用）
from wadeTools.wadeTools_Print import wadePrint, wadeRedPrint
from wadeTools import (
    wadeTools_lock, wadeTools_getSystemInfo,
)
from wadeTools.wadeTools_Print import wadePrint
import os
import time
import asyncio
import importlib.util

import lark_oapi as lark

from lark_oapi.api.im.v1 import P2ImMessageReceiveV1, CreateMessageRequest, CreateMessageRequestBody, CreateMessageResponse
from datetime import datetime, timedelta
import json
import requests

# --------------------------
# 配置应用凭证（替换为你的实际信息）
# --------------------------
APP_ID = "cli_a8104951b66b900c"  # 从开发者后台获取
APP_SECRET = "0AwayvK6wJMxjuwcDl8B2c1r5qPybEaw"  # 从开发者后台获取

# 全局变量存储访问令牌及过期时间
access_token = None
token_expire_time = None


class AutoTaskRunner:
    """自动发现并运行任务的本地库组件"""

    # def __init__(self, tasks_dir=r"F:\code\wadeTools\wadeTools\RobotTasks"):
    def __init__(self, tasks_dir="RobotTasks"):
        # 这表示tasks_dir是当前工作目录下的RobotTasks文件夹
        self.tasks_dir = tasks_dir
        self._load_tasks()  # 初始化时自动扫描任务

    def _load_tasks(self):
        """扫描 tasks/ 目录下所有任务文件并加载"""
        self.tasks = []
        if not os.path.exists(self.tasks_dir):
            os.makedirs(self.tasks_dir)
            return

        # 遍历目录下所有 .py 文件
        for filename in os.listdir(self.tasks_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                self._load_task_module(filename)

    def _load_task_module(self, filename):
        """加载单个任务模块"""
        module_name = filename[:-3]
        file_path = os.path.join(self.tasks_dir, filename)

        # 动态导入模块
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 检查模块是否包含 async run 函数（约定接口）
        if hasattr(module, "run") and asyncio.iscoroutinefunction(module.run):
            self.tasks.append(module.run)
            print(f"[自动发现任务] {filename}")

    async def run_all_tasks(self, message_data):
        """执行所有发现的任务"""
        if not self.tasks:
            return
        await asyncio.gather(*[task(message_data) for task in self.tasks])
# --------------------------
# 本地库的事件处理逻辑（永不修改）
# --------------------------
task_runner = AutoTaskRunner()  # 初始化自动任务运行器
# --------------------------
# 获取访问令牌
# --------------------------
def get_access_token():
    global access_token, token_expire_time

    # 检查令牌是否有效（提前30秒过期，避免网络延迟问题）
    if access_token and token_expire_time and datetime.now() < token_expire_time - timedelta(seconds=30):
        return access_token

    # 调用获取令牌接口
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET})

    response = requests.post(url, headers=headers, data=payload)
    result = response.json()

    if "tenant_access_token" in result:
        access_token = result["tenant_access_token"]
        # 设置过期时间
        token_expire_time = datetime.now() + timedelta(seconds=result["expire"])
        print("获取访问令牌成功")
        return access_token
    else:
        print(f"获取访问令牌失败: {result}")
        return None


# --------------------------
# 发送消息函数（使用requests实现）
# --------------------------
def send_message(chat_id: str, content: str, chat_type: str = "p2p"):
    """
    发送消息到飞书
    :param chat_id: 会话ID
    :param content: 消息内容（文本）
    :param chat_type: 会话类型，"p2p"表示单聊，"group"表示群聊
    """
    # 获取访问令牌
    token = get_access_token()
    if not token:
        print("无法获取访问令牌，发送消息失败")
        return

    # 构建请求参数
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    msg_content = {
        "text": content
    }
    req = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps(msg_content)
    }
    print(req)
    payload = json.dumps(req)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # 发送请求
    response = requests.post(url, params=params, headers=headers, data=payload)

    # 处理响应
    print(f"消息发送响应日志ID: {response.headers.get('X-Tt-Logid')}")
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            print(f"消息发送成功，消息ID: {result.get('data', {}).get('message_id')}")
        else:
            print(f"发送消息失败: {result}")
    else:
        print(f"发送请求失败，状态码: {response.status_code}，响应内容: {response.text}")


# --------------------------
# 消息事件处理函数（接收用户消息并回复）
# --------------------------
def handle_message(data: P2ImMessageReceiveV1) -> None:
    try:
        # 提取消息基本信息
        event = data.event
        chat_id = event.message.chat_id
        chat_type = event.message.chat_type  # "p2p"表示单聊，"group"表示群聊
        message_type = event.message.message_type
        message_id = event.message.message_id
        sender_id = event.sender.sender_id.user_id

        # 解析文本消息内容
        if message_type == "text":
            content = json.loads(event.message.content)["text"]
            print(f"\n=== 收到新消息 ===")
            # print(f"会话类型: {'单聊' if chat_type == 'p2p' else '群聊'}")
            # print(f"发送者 ID: {sender_id}")
            print(f"消息内容: {content}")
            # print(f"消息 ID: {message_id}")
            time.sleep(10)
            # 发送回复消息
            reply_content = f"已收到你的消息: {content}"
            # send_message(chat_id, reply_content, chat_type)

            # 发送消息给手机
            send_feishu_message(message_content=content)
        else:
            print(f"\n=== 收到不支持的消息类型 ===")
            print(f"类型: {message_type}, 消息 ID: {message_id}")

    except Exception as e:
        print(f"处理消息时出错: {str(e)}")

def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    event = data.event
    message_type = event.message.message_type
    if message_type == "text":
        content = json.loads(event.message.content)["text"]
        print(f"\n=== 🤖收到新消息 ===")
        # print(f"会话类型: {'单聊' if chat_type == 'p2p' else '群聊'}")
        # print(f"发送者 ID: {sender_id}")
        print(f"🤖消息内容: {content}")
        asyncio.create_task(task_runner.run_all_tasks(content))
    # print(f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data, indent=4)}')
# --------------------------
# 处理机器人进入单聊事件时发送欢迎消息
# --------------------------
# def handle_bot_enter_p2p(data: lark.CustomizedEvent) -> None:
#     try:
#         print(f"\n=== 机器人进入单聊会话 ===")
#         # 提取会话ID
#         chat_id = data.event.get("chat_id")
#         if chat_id:
#             # 发送欢迎消息
#             welcome_msg = "你好！我是你的助手，有什么可以帮助你的吗？"
#             send_message(chat_id, welcome_msg)
#
#         print(f"事件数据: {lark.JSON.marshal(data, indent=2)}")
#     except Exception as e:
#         print(f"处理进入单聊事件时出错: {str(e)}")
#

# --------------------------
# 注册所有事件处理器
# --------------------------
event_handler = (lark.EventDispatcherHandler.builder("", "")
                 # .register_p2_im_message_receive_v1(handle_message)
                .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
                 # .register_p2_customized_event("im.chat.access_event.bot_p2p_chat_entered_v1",
                 #    handle_bot_enter_p2p)
                 .build())


# --------------------------
# 独立函数，机器人给手机发送消息用的
# --------------------------
def send_feishu_message(message_content="旺旺", msg_type="text"):
    APP_ID = "cli_a8104951b66b900c"  # 从开发者后台获取
    APP_SECRET = "0AwayvK6wJMxjuwcDl8B2c1r5qPybEaw"  # 从开发者后台获取
    RECEIVE_ID = "ou_3777a45bad41aeb30508665ba04678db"  # 接收者ID（用户ID或群组ID）这个id是在发送消息开放文旦中 右边查询参数找到的，每个用户一个
    # MESSAGE_CONTENT = "旺旺"  # 消息内容
    def get_app_access_token(app_id, app_secret):
        """获取飞书自建应用的app_access_token和tenant_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = {"app_id": app_id, "app_secret": app_secret}

        try:
            response = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(payload)
            )
            result = response.json()

            if result.get("code") == 0:
                return {
                    "success": True,
                    "app_access_token": result.get("app_access_token"),
                    "tenant_access_token": result.get("tenant_access_token"),
                    "expire": result.get("expire")
                }
            else:
                return {
                    "success": False,
                    "error_code": result.get("code"),
                    "error_msg": result.get("msg")
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error_msg": f"网络请求异常: {str(e)}"
            }

    # 1. 获取token（可选，SDK内部会自动处理token获取）
    token_info = get_app_access_token(APP_ID, APP_SECRET)
    if token_info["success"]:
        pass
        print("获取Token成功:")
        print(f"app_access_token: {token_info['app_access_token']}")
        print(f"有效期: {token_info['expire']}秒")
    else:
        print(f"获取Token失败: {token_info['error_msg']}")

    # 2. 发送消息
    # print("\n🤖开始发送消息...")
    # send_feishu_message(
    #     app_id=APP_ID,
    #     app_secret=APP_SECRET,
    #     receive_id=RECEIVE_ID,
    #     message_content=MESSAGE_CONTENT
    # )

    # 创建client
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .log_level(lark.LogLevel.ERROR) \
        .build()
    content = f'{{"text": "{message_content}"}}'
    # 构造请求对象
    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type("open_id") \
        .request_body(CreateMessageRequestBody.builder()
                      .receive_id(RECEIVE_ID)
                      .msg_type(msg_type)
                      .content(content)
                      .build()) \
        .build()

    # 发起请求
    response: CreateMessageResponse = client.im.v1.message.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    # lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    print(f"🤖:{message_content}")


# --------------------------
# 启动长连接客户端
# --------------------------
def main():
    # 初始化长连接客户端（用于接收消息）
    client = lark.ws.Client(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO  # 日志级别：INFO/DEBUG
    )

    print("机器人已启动，等待接收消息...（按 Ctrl+C 停止）")
    client.start()  # 启动长连接，持续监听事件
    # send_message("oc_66cebc864299922073d58b421f01cd13", "123", "p2p")


if __name__ == "__main__":
    main()
