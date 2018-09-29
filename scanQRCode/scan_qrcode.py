from ctypes import *  # cdll, c_int
import numpy as np
import cv2
import os

lib = cdll.LoadLibrary(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libtdc3.so'))


class ocr_qrcode(object):
    def __init__(self):
        self.obj = lib.barcode_new()

    def callocrtdc(self, img_data, im_w, im_h, roi_x, roi_y, roi_w, roi_h, info):
        lib.scan_qrcode(self.obj, img_data, im_w, im_h, roi_x, roi_y, roi_w, roi_h, info)


"""
recognize qrcode image
image: numpy array
roi: [x,y,width,height]
"""


def recog_qrcode(image, roi=None, use_enh=False):
    if len(image.shape) > 2:
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if image.shape[0] % 16 != 0 and image.shape[1] % 16 != 0:
        image = cv2.resize(image, (int(image.shape[1] / 16) * 16, int(image.shape[0] / 16) * 16))

    im_w = image.shape[1]
    im_h = image.shape[0]
    if roi is None:
        roi_x = 0
        roi_y = 0
        roi_w = im_w
        roi_h = im_h
    else:
        roi_x = roi[0]
        roi_y = roi[1]
        roi_w = roi[2]
        roi_h = roi[3]

    img_data = image.ctypes.data_as(POINTER(c_ubyte))
    c_im_w = c_int(im_w)
    c_im_h = c_int(im_h)
    c_roi_x = c_int(roi_x)
    c_roi_y = c_int(roi_y)
    c_roi_w = c_int(roi_w)
    c_roi_h = c_int(roi_h)
    str_num = 2048
    c_info = (c_byte * str_num)()
    c_pos = (c_int * 8)()

    if use_enh is False:
        lib.orc_qrcode(img_data, c_im_w, c_im_h, c_roi_x, c_roi_y, c_roi_w, c_roi_h, c_info, c_pos)
    else:
        lib.orc_qrcode_ex(img_data, c_im_w, c_im_h, c_roi_x, c_roi_y, c_roi_w, c_roi_h, c_info, c_pos)

    str_info = []
    for i in range(2048):
        if c_info[i] == 0:
            break
        if c_info[i] < 0:
            str_info.append('?')
        else:
            str_info.append(chr(c_info[i]))
    position = list()
    position.append([c_pos[0], c_pos[1]])
    position.append([c_pos[2], c_pos[3]])
    position.append([c_pos[4], c_pos[5]])
    position.append([c_pos[6], c_pos[7]])

    return ''.join(str_info), position


def contrast_brightness(img, c, b):
    rows, cols = img.shape[:2]
    blank = np.zeros([rows, cols], img.dtype)
    dst = cv2.addWeighted(img, c, blank, 1 - c, b)
    return dst


def recog_qrcode_ex(image, roi=None):
    if roi is not None:
        img = image[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
    else:
        img = image

    print('the first try')
    kerl = np.ones((3, 3), np.uint8)
    en_img = cv2.dilate(img, kerl, iterations=1)
    en_img = cv2.erode(en_img, kerl, iterations=1)
    info, pos = recog_qrcode(en_img)

    if info is '':
        print('the second try')
        en_img = cv2.erode(img, kerl, iterations=1)
        en_img = cv2.dilate(en_img, kerl, iterations=1)
        info, pos = recog_qrcode(en_img)

    if info is '':
        print('the third try')
        height, width = img.shape[:2]
        ratio = 2
        en_img = cv2.resize(img, (int(width * ratio), int(height * ratio)))
        en_img = cv2.bilateralFilter(en_img, 20, 20, 100)
        # en_img = cv2.GaussianBlur(img, (5, 5), 0)
        en_img = cv2.erode(en_img, kerl, iterations=1)
        en_img = cv2.dilate(en_img, kerl, iterations=1)
        en_img = contrast_brightness(en_img, 1.3, 1)
        cv2.imwrite('./tmp1.jpg', en_img)
        ret, en_img = cv2.threshold(en_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        en_img = cv2.dilate(en_img, kerl, iterations=1)

        # cv2.imwrite('./tmp.jpg',en_img)
        info, pos = recog_qrcode(en_img)

        for i in range(4):
            pos[i][0] = int(pos[i][0] / ratio)
            pos[i][1] = int(pos[i][1] / ratio)

    if info is '':
        print('the 4th try')
        for j in range(50):
            info, pos = recog_qrcode(en_img, use_enh=True)
            if info is not '':
                break

    if info is '':
        print('the 5th try')
        en_img = img.copy()
        for j in range(50):
            info, pos = recog_qrcode(en_img, use_enh=True)
            if info is not '':
                break

    if info is '':
        print('the 6th try')
        for i in range(5, 20):
            bn_img = img.copy()
            ret, bn_img = cv2.threshold(bn_img, i * 10, 255, cv2.THRESH_BINARY)
            info, pos = recog_qrcode(bn_img)
            if info is not '':
                break

    if roi is not None:
        for i in range(4):
            pos[i][0] += roi[0]
            pos[i][1] += roi[1]

    return info, pos


if __name__ == "__main__":
    image = cv2.imread("./code.png", 0)
    str_info = recog_qrcode(image, roi=None)
    print("info:", str_info)
