import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6fde63b6e8474910bf94c5dc32d9ed55",
    base_url="https://api.deepseek.com",
)

completion = client.chat.completions.create(
    # model="deepseek-chat",
    model="deepseek-reasoner",
    messages=[
        {
                "role": "system",
                "content": """用户给你一个商品的链接，要用搜索的方式，整合内容搜索百度，写一篇商品评测文章，我要把你的内容作为api数据，请不要加入额外的语言，这个链接是测评的对象，你要分析京东商品内容，查找竞品商品进行对比
格式要求：
第一，title：写一个标题，10到20子字的标题
第二，content：文章写2000字，内容结合搜索的内容，纵横对比，段落间留 @照片@ 的标记三个，方便我替换换成图片
第三，文章视角是使用用户的真实反馈，有配置表格，有专业优劣点评，不要看着像广告，并提取其中的关键信息，
写作要求：
1. **塑造写作个性**：“试着用那种轻松自然的语气来写，想象自己是个28岁的新媒体达人，时不时地用‘哈哈’、‘emmm’、‘说实话’这样的口语化词汇。最关键的是，要像在和朋友聊天一样自然。”
2. **调整语言风格**：“写作的时候记得：1.多用短句；2.避免太正式的词汇；3.可以用反问、感叹等口语化表达；4.适当加点幽默；5.用具体的例子来代替抽象的概念。”
3. **结尾互动**：“结尾的时候要有互动感，比如问‘你们有没有遇到类似的问题？’、‘欢迎在评论区分享你的经历’，让读者感到参与其中。”
以 JSON 的形式输出，输出的 JSON 需遵守以下的格式：\n\n{\n  \"title\": <10到20子字的标题>,\n  \"itemID\": <商品的链接>,\n  \"content\": <文章内容>\n}"""
        },
        {
                "role": "user",
                "content": "https://item.jd.com/100103222748.html"
        }
    ]
)

print(completion.choices[0].message.content)