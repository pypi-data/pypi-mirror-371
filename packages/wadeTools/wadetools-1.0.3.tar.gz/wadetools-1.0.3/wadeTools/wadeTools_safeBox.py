# 安装库,这个是加密授权模块
# pip install cryptography
# cryptography 版本43.0.1
import requests
from urllib.parse import urlencode
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
from base64 import b64decode
import random
import uuid
import os
# from wadeTools.wadeTools_Print import wadePrint

http_url = "https://vip1.eydata.net"

"""请求函数"""
def http_post(url, data):  # 请求函数
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if not url.startswith('/'):
            url = '/' + url
        url_encoded = urlencode([(key, value) for key, value in data.items()])
        r = requests.post(http_url + url, data=url_encoded, headers=headers, timeout=30)
        if r.status_code == 200:
            result = str(r.text)
        else:
            result = "遇到错误，请检查网络重试"
        return result
    except Exception as e:
        print(e)
        return "遇到错误，请检查网络重试"

"""加密函数"""
def SingleLogin_encrypt_Up_41342_dict(parameters, keys):
    """加密函数"""
    def SingleLogin_encrypt_Up_41342(value, keys):
        def import_pem_public_key(pem_string):
            pem_data = pem_string.encode('utf-8')
            public_key = serialization.load_pem_public_key(
                pem_data,
                backend=default_backend()
            )
            return public_key

        pem_key = """  
    -----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQ/XeeE7cmyFf4WOdbd0FTCzm8
    Q0gksLttMouVsV7iGZfUwqIeCZ9XzGeiriBlaVuDILS9a1g8WNdtFJqHwvOFto8d
    78Sl1ge1A+qBxo7FxgcCLt57p/8qc0hX/QliFfmveD/fE2EZ1Cvs9/84kzzL2f7i
    mpJRO/ZvAc8YO0iNFQIDAQAB
    -----END PUBLIC KEY-----
    """
        public_key = import_pem_public_key(pem_key)
        original_data_bytes = value.encode('utf-8')
        for key in keys:
            original_data_bytes = bytes([b ^ key % 256 for b in original_data_bytes])
        keys_bytes = bytes([len(keys)]) + bytes([k % 256 for k in keys])
        encrypted_data_with_keys = keys_bytes + original_data_bytes
        key_size = public_key.public_numbers().n.bit_length() // 8
        block_size = key_size - 11
        encrypted_data = b''
        offset = 0
        while offset < len(encrypted_data_with_keys):
            block = encrypted_data_with_keys[offset:offset + block_size]
            encrypted_block = public_key.encrypt(
                block,
                padding.PKCS1v15()
            )
            encrypted_data += encrypted_block
            offset += block_size
        return b64encode(encrypted_data).decode('utf-8')

    params_str = '&'.join([f"{k}={v}" for k, v in parameters.items()])
    encrypted_params = SingleLogin_encrypt_Up_41342(params_str, keys)
    return {"p": encrypted_params}

"""解密函数"""
def SingleLogin_decrypt_Down_41342(value, keys):
    """解密函数"""
    def import_pem_private_key(pem_string):
        private_key = serialization.load_pem_private_key(
            pem_string,
            password=None,
            backend=default_backend()
        )
        return private_key

    key = b"""
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCCN2U+CfDcY3XEZOKYKd3DoqcEojo51X7YaCcx0tsnZbsDgrlF
dQxQdEyUtuDGdBtu2BxzNffy0fnusIagMvvvDSr5d0HrYd1qEMvAhEFVN8W23teK
ugPAjW3UxhqjUZ+/RAEJBPD37qCzZLkrwzLSQ9OHdsWkDvAX/kVVR7CCTwIDAQAB
AoGANtlIjuI3D03hrDDmdTulSqN3gG8o4XV5MYRlhgoP/79ND8R/b69G2ZizLSz+
7vi3GXB0Q18nKqOhiBXZDx+KmF2Kjnk+0m2l3VuVh7davpJH1aD8dnIE/p3B4oNs
mPjK2v4I+t+Wh5+kuJ48uCwtRMZgZM5h+JVBIIDdaqRU1iECQQDzrn/fz2cltxq2
RzbGNkcpnmpOOr2IjtNsUMhf4VpcGTC0MMeMcRSBJ0MI1EfkC1gHf0sfeeEnInEs
noFWdN0xAkEAiMyI1uBnRzXfBG5hZMU76dWBjA7rYkKS1XRBcSDrWy9xIMxq03h8
bFlb2vC/UzgyyQS9cSctT0NiHp1dMfV3fwJASm9sSj59gIzNEQ7x0Vw1IqZsTJcu
3C7csEKA4qDgzC85rGEWI3VLUSRgGqtVhnhcnHWqyeOd/ilMLtgAJBuwkQJAfniB
5g4uzUH7vdACkLRb0LIIA6FjckNUFq1VNy6VCIdS0lzKQlm4xj7S0hYS+/AP25Jb
RfpPRGFqnB0mJOLoJwJBAKv77NrHL9V6qpbPlG4oyKMbkA2LN5flyW8al4h///4c
aY9K8KBNjaQxBxBKkvJq2tRyb6oxYE6BBloRZXJmTt0=
-----END RSA PRIVATE KEY-----

"""
    private_key = import_pem_private_key(key)

    def rsa_decrypt(private_key, ciphertext):
        return private_key.decrypt(
            ciphertext,
            padding.PKCS1v15()
        )

    encrypted_data = b64decode(value)
    decrypted_data = b''
    key_size = 1024 // 8
    block_size = key_size
    offset = 0
    while offset < len(encrypted_data):
        block = encrypted_data[offset:offset + block_size]
        decrypted_block = rsa_decrypt(private_key, block)
        decrypted_data += decrypted_block
        offset += block_size
    if len(keys) > 8:
        keys = keys[:8]
    for key in keys:
        xor_key = key % 256
        decrypted_data = bytes([b ^ xor_key for b in decrypted_data])
    return decrypted_data.decode('utf-8')

"""登陆模块"""
def login(apiUrl):
    if os.path.exists('card_code.txt'):
        with open('card_code.txt', 'r') as file:
            single_code = file.read().strip()
    else:
        single_code = input("请输入卡密: ")
        with open('card_code.txt', 'w') as file:
            file.write(single_code)
    # 获取MAC地址
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:]
    # print(mac_address)
    data = {
        'SingleCode': single_code,
        'Ver': '1.0',
        'Mac': mac_address,
    }

    # # 示例
    # data = {
    #     'SingleCode': 'OE1AF8F5EFE238EAFCA79894A7AF02DE',
    #     'Ver': '1.0',
    #     'Mac': '',
    # }
    keys = [random.randint(1, 255) for _ in range(random.randint(3, 5))]
    encrypted_parameters = SingleLogin_encrypt_Up_41342_dict(data, keys)
    encrypted_parameters['api'] = "41342"

    ret = http_post(f'/{apiUrl}', encrypted_parameters)
    # wadePrint(ret)

    decrypted_ret = SingleLogin_decrypt_Down_41342(ret, keys)
    # wadePrint(decrypted_ret)
    def split_decrypted_ret(decrypted_ret):
        # 使用 '|' 分割返回的内容
        parts = decrypted_ret.split('|')
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            raise ValueError("返回的内容格式不正确")

    # print(ret)
    code, expiration_time = split_decrypted_ret(decrypted_ret)

    # print("代码：", code)
    # print("当前时间：", expiration_time)

    if len(code) == 32:
        print('登录成功，当前时间：' + expiration_time)
        url = 'https://vip1.eydata.net/0256394C26CC5CCF'  # 移除了错误的字符
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6,zh;q=0.4',
            'Cookie': 'c=cookie; c1=cookie1; c2=cookie2'
        }
        data = {
            'StatusCode': single_code,
            'UserName': single_code  # 使用字典格式来组织数据
        }

        response = requests.post(url, headers=headers, data=data)

        print(f'到期时间' + response.text)
        return True
    else:
        print('登录失败，错误码：' + ret)
        file_path = os.path.join('card_code.txt')

        # 检查文件是否存在
        if os.path.exists(file_path):
            # 删除文件
            os.remove(file_path)
            print(f"文件 {file_path} 已被删除。")
        else:
            print(f"文件 {file_path} 不存在。")
        return False

"""卡密模块封装"""
def safeBox(apiUrl):
    """
    验证卡密是否可用，需要的FFBAEA4E4AA82CCD是易游网络验证的验证api，灵活替换
    调用用法：
    safeBox(apiUrl="FFBAEA4E4AA82CCD")
    xxxx程序代码
    """
    try:
        while not login(apiUrl):
            pass
    except Exception as e:
        print(f"登录验证出现异常: {e}")
if __name__ == '__main__':
    safeBox(apiUrl="FFBAEA4E4AA82CCD")
    print("验证通过")