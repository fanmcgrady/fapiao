import copy
import math
import os

import cv2

from home.utils import Detect
from home.utils import detectType
from home.utils import flow
import fp
import lineToAttribute.getAtbt


def de_muban(muban, area_rate=0.8):
    """
    :param muban: 模板字典，[key:[x,y,width,height]]
    :param area_rate: 新模板和旧模板面积比例，小于1为缩小
    :return: 新模板字典
    """
    for key in muban:
        lst = muban[key]
        x = lst[0]
        y = lst[1]
        width = lst[2]
        height = lst[3]
        rate = 1 - math.sqrt(area_rate)
        de_width = rate * width / 2
        de_height = rate * height / 2
        new_x = x + de_width
        new_y = y + de_height
        new_width = width - rate * width
        new_height = height - (rate * height) * 2
        muban[key] = [new_x, new_y, new_width, new_height]
    return muban


def init(filename):
    midProcessResult = detectType.detectType('allstatic', filename)  # tangpeng 预处理
    # 行提取
    blueTemplet = {
        'departCity': [48, 62, 222, 56],
        'arriveCity': [412, 61, 228, 55],
        'trainNumber': [264, 62, 170, 57],
        'invoiceDate': [24, 139, 369, 42],
        'seatNum': [408, 138, 160, 40],
        'idNum': [22, 276, 306, 38],
        'passenger': [328, 276, 150, 38],
        'totalAmount': [33, 177, 151, 39],
        'ticketsNum': [21, 10, 195, 66]
    }

    redTemplet = {
        'departCity': [29, 74, 218, 54],
        'arriveCity': [425, 68, 224, 64],
        'trainNumber': [230, 65, 203, 62],
        'invoiceDate': [0, 163, 357, 41],
        'seatNum': [392, 164, 203, 46],
        'idNum': [0, 343, 350, 45],
        'totalAmount': [3, 206, 212, 52],
        'ticketsNum': [34, 40, 202, 47]
    }

    blueTemplet = de_muban(blueTemplet, area_rate=0.9)
    redTemplet = de_muban(redTemplet, area_rate=0.9)

    TemType = blueTemplet  # 默认蓝票
    if midProcessResult[1] == 1:
        TemType = blueTemplet

    if midProcessResult[1] == 2:
        TemType = redTemplet

    Templet = adjustToTextLine(TemType, Detect.detect(cv2.imread(midProcessResult[0]), 1), midProcessResult[1])  # 火车票

    attributeLine = lineToAttribute.getAtbt.compute(textline(midProcessResult[0]), Templet)

    jsonResult = flow.cropToOcr(midProcessResult[0], attributeLine, midProcessResult[1])  # ocr和分词
    print(jsonResult)
    return jsonResult, midProcessResult[1]


def textline(filepath):
    # --- 初始化 ---
    # 读取文件夹下图片
    # dset_dir = 'E:/DevelopT/pycharm_workspace/Ocr/pic'
    # jpgs = fp.util.path.files_in_dir(dset_dir, '.jpg')
    # jpgs = filepath
    # fp.util.path.files_in_dir(filepath)
    # 创建 字符行检测器 （检测结果为：若干可能为字符行的矩形框）
    detect_textlines = fp.frame.textline.Detect()
    # 创建 字符行分类器 （分类结果为：印刷字符、针式打印字符等）
    # classify_textlines = fp.frame.textline.Classify()
    # print(jpgs[0])
    # 读第一个图片
    im = cv2.imread(filepath, 0)
    # 检测字符行，并分类
    rects = detect_textlines(im)

    # 绘制结果
    vis_textline0 = fp.util.visualize.rects(im, rects)
    # vis_textline1 = fp.util.visualize.rects(im, rects, types)
    # 显示
    '''pl.figure(figsize=(15, 10))
    pl.subplot(2, 2, 1)
    pl.imshow(im, 'gray')

    pl.subplot(2, 2, 2)
    pl.imshow(vis_textline0)
    pl.show()'''

    return rects


def adjustToTextLine(mubandict, box, typeT):  # box顺序需要调整

    midbox = sortBox(box)
    mubanBox = []
    if typeT == 1:
        mubanBox = [526, 272, 634, 379]  # [x1,y1,x2,y2]
    if typeT == 2:
        mubanBox = [483, 259, 632, 439]

    w = midbox[2] - midbox[0]
    h = midbox[3] - midbox[1]

    for x in mubandict:
        tempArray = copy.deepcopy(mubandict[x])
        mubandict[x][0] = midbox[2] - (int)((mubanBox[2] - tempArray[0]) / (mubanBox[2] - mubanBox[0]) * w)
        mubandict[x][1] = midbox[3] - (int)((mubanBox[3] - tempArray[1]) / (mubanBox[3] - mubanBox[1]) * h)
        mubandict[x][2] = tempArray[2] / (mubanBox[2] - mubanBox[0]) * w
        mubandict[x][3] = tempArray[3] / (mubanBox[3] - mubanBox[1]) * h

    return mubandict


def sortBox(box):
    # box[[536, 387], [534, 280], [641, 279], [643, 386]]
    a = []
    b = []
    for x in box:
        a.append(x[0])
        b.append(x[1])

    return [min(a), min(b), max(a), max(b)]

if __name__ == "__main__":
    init('Image_065.jpg')
