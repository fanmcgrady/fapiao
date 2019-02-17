import base64
import sys

import numpy as np

sys.path.append("/home/huangzheng/ocr")

import copy
import json
import cv2
# import InterfaceType
from InterfaceType import JsonInterface

from scanQRCode.scan_qrcode import recog_qrcode, recog_qrcode_ex
import fp.TextBoxes.recog_invoice_type
import caffe


def getArrayFromStr(strRes):
    sR = copy.deepcopy(strRes)
    index = sR.find(',', 0)
    resultArray = []
    while index >= 0:
        resultArray.append(sR[:index])
        sR = sR[index + 1:]
        index = sR.find(',', 0)
    resultArray.append(sR)
    return resultArray


def scanQRc(filepath):
    image = cv2.imread(filepath, 0)

    str_info, position, state = recog_qrcode(image, roi=None)
    print("info:", str_info)
    print("pos:", position)

    # ***** if conventnal method is invalid ******
    # ***** then use the enhanced method   *******
    if str_info is '':
        height, width = image.shape[:2]
        roi = [0, 0, int(width / 4), int(height / 4)]
        # roi = None
        str_info, position, state = recog_qrcode_ex(image, roi)
        print("info(ex):", str_info)
        print("pos(ex):", position)
    # ***** **************************************

    return str_info, position


# 识别二维码
def runQR(filepath):
    try:
        info, position = scanQRc(filepath)
    except:
        return None

    if info != '':

        resArray = getArrayFromStr(info)
        # js = InterfaceType.JsonInterface.invoice()
        js = JsonInterface.invoice()
        js.setVATInvoiceFromArray(resArray, "special")

        jsoni = js.dic['invoice']
        print(jsoni)
        return json.dumps(jsoni).encode().decode("unicode-escape")
    else:
        return None


# 识别类型
def runType(filepath):
    try:
        recog = fp.TextBoxes.recog_invoice_type.InvoiTypeRecog()
        im = caffe.io.load_image(filepath)

        invoice_type = ['quota', 'elect', 'airticket', 'spec_and_normal', 'spec_and_normal_bw', 'trainticket']
        typeP = invoice_type[recog(im)]
    except:
        return "other"

    if typeP == 'spec_and_normal' or typeP == 'spec_and_normal_bw':
        typeP = 'special'

    return typeP


def base64str_to_im(img_data_str):
    img_byte = base64.b64decode(img_data_str)
    img_np_arr = np.fromstring(img_byte, np.uint8)
    im = cv2.imdecode(img_np_arr, cv2.IMREAD_COLOR)
    return im


def delete_hand(img_im):
    ret_text = post_for_bbox(img_im)
    handObj = json.loads(ret_text)
    if handObj['status'] == 'success':
        body = handObj['body']
        if 'hand' not in body:
            return
        hands = body['hand']
        for hand in hands:
            cv2.rectangle(img_im, (hand[0], hand[1]), (hand[2], hand[3]), (0, 255, 0), 1)
            # logger.info(hand)
    # logger.info(handObj)
    cv2.imshow('pic', img_im)


if __name__ == '__main__':
    filepath = "Image_00175.jpg"
    cv2_img = cv2.imread(filepath)

    base64_str = base64.b64encode(cv2.imencode('.jpg', cv2_img)[1]).decode()
    print(base64_str)

    # runType(filepath)
