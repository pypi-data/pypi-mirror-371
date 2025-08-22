import re


def extract_jd_product_id(url):
    # 正则匹配，支持item.jd.com和mitem.jd.hk等域名
    # 匹配规则：
    # - 支持item.jd.com或mitem.jd.hk等域名
    # - 支持/product/路径或直接跟商品ID的情况
    pattern = r'(?:item(?:\.m)?\.jd\.com|mitem\.jd\.hk)/(?:product/)?(\d+)\.html'
    match = re.search(pattern, url)

    if match:
        product_id = match.group(1)  # 提取第一个捕获组的内容
        print(f"提取的商品ID：{product_id}")
        return product_id
    else:
        print("未找到匹配的商品ID")
        return None


# 测试
url1 = "https://mitem.jd.hk/product/100017184844.html?cu=true&utm_source=lianmeng__9__kong&utm_medium=jingfen&utm_campaign=t_1001706833_&utm_term=e6cabdf3c43d4420a21225b54e5b9730&scid=3bc8b325-42a3-437f-ae70-def46708cabc"
url2 = "https://item.jd.com/product/100015760597.html"
url3 = "https://item.m.jd.com/100015760598.html"

extract_jd_product_id(url1)  # 应输出：100017184844
extract_jd_product_id(url2)  # 应输出：100015760597
extract_jd_product_id(url3)  # 应输出：100015760598
