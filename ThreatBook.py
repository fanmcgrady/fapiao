# 增值税发票二维码识别接口
import base64

import requests

HOST = "http://202.115.103.60"


# 发票二维码识别接口
def run_qrcode():
    url = HOST + '/qr_api'

    file_name = "Image_00175.jpg"
    with open(file_name, "rb") as f:
        base64_data = base64.b64encode(f.read())
        print(base64_data)
    params = {
        'picture': base64_data
    }
    response = requests.post(url, data=params)
    return response.json()


# 发票分类接口
def run_type():
    url = HOST + '/type_api'

    file_name = "Image_00175.jpg"
    with open(file_name, "rb") as f:
        base64_data = base64.b64encode(f.read())
        print(base64_data)

    params = {
        'picture': base64_data
    }

    response = requests.post(url, data=params)
    return response.json()


if __name__ == '__main__':
    # print(run_qrcode())
    print(run_type())
