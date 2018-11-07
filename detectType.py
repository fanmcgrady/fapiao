import os

import cv2
import numpy as np

import fp.core
import fp.frame
import fp.train_ticket


# %matplotlib inline


def jwkj_get_filePath_fileName_fileExt(filename):  # 提取路径
    (filepath, tempfilename) = os.path.split(filename);
    (shotname, extension) = os.path.splitext(tempfilename);
    return filepath, shotname, extension

def detectType(dset_root, file_name):
    file = os.path.join(dset_root, file_name)
    raw_im = cv2.imread(file, 1)

    # 初步矫正
    detect = fp.frame.surface.Detect()

    # 检查是否上下颠倒火车票
    is_upside_down = fp.train_ticket.train_ticket.UpsideDownCheck_v2()

    # 检测提取
    out_im = detect(raw_im)
    # 是否上下颠倒，是则旋转180°
    if is_upside_down(out_im):
        # 旋转
        std_out_im = fp.core.trans.rotate180(out_im)
    else:
        std_out_im = out_im

    out_filename = file_name.replace('upload', 'out')
    out_filename = os.path.join(dset_root, out_filename)

    cv2.imwrite(out_filename, std_out_im)

    blue_ticket = fp.train_ticket.is_blue(out_im)  # blue or red ticket

    if blue_ticket:
        flag = 1
    else:
        flag = 2

    return out_filename, flag

'''
dset_root = '/home/tangpeng/fapiao/dataset/scan_for_locate'
'''
# detectType('Image_065.jpg')

# test
# print(detectType('Image_065.jpg'))
