from wadeTools.wadeTools_Print import wadePrint, wadeRedPrint, wadeBluePrint


def wadeDeepSeek(content):
    import os
    from openai import OpenAI

    client = OpenAI(
        # 请用知识引擎原子能力API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-KxoONWmmQHhiiFtJrqYb7u49qb3YCZGSrtTTo9UBQPF3rtsQ",  # 如何获取API Key：https://cloud.tencent.com/document/product/1772/115970
        base_url="https://api.lkeap.cloud.tencent.com/v1",
    )

    completion = client.chat.completions.create(
        model="deepseek-r1",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        messages=[
            {'role': 'user', 'content': f'{content}'}
        ]
    )

    # 通过reasoning_content字段打印思考过程
    wadeBluePrint("思考过程：")
    print(completion.choices[0].message.reasoning_content)
    # 通过content字段打印最终答案
    wadeBluePrint("最终答案：")
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def wadeGetGPT(content):
    import requests
    import json

    url = "https://api.lightai.io/v1/chat/completions"

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content":f"{content}"
            }
        ]
    })
    headers = {
        'TE': 'trailers',
        'Authorization': 'Bearer sk-WusbK0hWlw5GVqBt195c04B674B940B2AbC84d2c4aF82c4b',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    return response.json()

def ollama(content):

if __name__ == '__main__':
    # from wadeTools.wadeTools_UserJSON import get_dict_by_key
    # wadePrint(get_dict_by_key(wadeGetGPT("美的空调 家电国家补贴 酷省电 大1.5匹 新一级能效 变频冷暖 节能 卧室壁挂式挂机 KFR-35GW/N8KS1-1   # 角色 你是一位超级擅长创作口水鸡汤风格爆款标题的知乎和小红书大师级作者。当接收到京东商品标题或者京东链接时，你要像魔法精灵一样，充分施展创意魔法，把它变成极具吸引力、完美契合口水鸡汤风格且能大幅提升点击率，字数在15到20字之间的爆款标题，且标题中尽量出现商品型号。## 技能 ### 技能1: 炮制爆款标题1. 若收到的是京东链接，调用插件京东购物 / jdshop学习该商品内容，务必精准获取商品型号；若收到的是京东商品标题，则直接开启深度剖析模式。精准抓住商品的独特卖点、能满足的情感需求以及目标受众的心理痛点。2. 调用百度插件，搜索该商品关键词，找出同类型且让消费者难以判断买哪个的对标商品。以温暖、励志、引人共鸣的口水鸡汤风格语言为基石，融入网络流行元素、情感钩子等点击率高的标题创作技巧，将对标商品与该商品对比，精心打造一个字数在15到20汉字之间且尽量包含商品型号的爆款标题。3. 确保创作的标题能瞬间抓住读者眼球，激发他们强烈的好奇与情感共鸣，促使他们迫不及待想要一探究竟。## 限制:- 创作范围严格限定在接收到的京东商品标题或京东链接相关商品，对其他无关话题一概不予理会。- 输出必须是完全原创、紧扣口水鸡汤风格且符合高点击率标题范式，字数在15到20字之间的内容，杜绝抄袭和机械应付。  每次的创作要有新意，用哪个好，怎么样，等爆款来结尾"),'content'))
    wadeDeepSeek(content='你好')
