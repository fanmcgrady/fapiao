import copy

import cv2
import matplotlib.pyplot as pl

import fp
import lineToAttribute.getAtbt
from home.utils import Detect
from home.utils import detectType
from home.utils import flow
from home.utils import muban


# 矫正 -> 行提取 -> ocr
def init(filename):
    # 矫正 -> 行提取
    out_file, flag, attributeLine = surface(filename)

    # ocr和分词
    jsonResult = flow.cropToOcr(out_file, attributeLine)
    return jsonResult, flag

def ocrWithoutSurface(out_file, line_result):
    # ocr和分词
    jsonResult = flow.cropToOcr(out_file, line_result)
    return jsonResult

# 矫正 -> 行提取
def surface(filename):
    # 预处理
    midProcessResult = detectType.detectType('allstatic', filename)
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

    TemType = blueTemplet  # 默认蓝票
    if midProcessResult[1] == 1:
        TemType = blueTemplet

    if midProcessResult[1] == 2:
        TemType = redTemplet

    Templet = adjustToTextLine(TemType, Detect.detect(cv2.imread(midProcessResult[0]), 1), midProcessResult[1])  # 火车票

    attributeLine = lineToAttribute.getAtbt.compute(textline(midProcessResult[0]), Templet)

    # 绘制行提取结果
    plt_rects = []
    for x in attributeLine:
        plt_rects.append(attributeLine[x])
    # 显示
    vis_textline0 = fp.util.visualize.rects(cv2.imread(midProcessResult[0], 0), plt_rects)
    pl.imshow(vis_textline0)
    # 保存到line目录
    pltpath = midProcessResult[0].replace("out", "line")
    pl.savefig(pltpath)

    return midProcessResult[0], midProcessResult[1], attributeLine


def textline(filepath):
    # --- 初始化 ---
    # 读取文件夹下图片
    # dset_dir = 'E:/DevelopT/pycharm_workspace/Ocr/pic'
    # jpgs = fp.util.path.files_in_dir(dset_dir, '.jpg')
    # jpgs = filepath
    # fp.util.path.files_in_dir(filepath)
    # 创建 字符行检测器 （检测结果为：若干可能为字符行的矩形框）

    thresh_pars = dict(mix_ratio=0.1, rows=1, cols=3, ksize=11, c=9)
    train_ticket_pars = dict(thresh_pars=thresh_pars, char_expand_ratio=0.4)
    detect_textlines = fp.frame.textline.Detect(pars=train_ticket_pars, debug=True)
    # 创建 字符行分类器 （分类结果为：印刷字符、针式打印字符等）
    # classify_textlines = fp.frame.textline.Classify()
    # print(jpgs[0])
    # 读第一个图片
    im = cv2.imread(filepath, 0)
    # 检测字符行，并分类
    rects = detect_textlines(im)

    # 绘制结果
    # vis_textline0 = fp.util.visualize.rects(im, rects)
    # vis_textline1 = fp.util.visualize.rects(im, rects, types)

    # 显示
    # pl.figure(figsize=(15, 10))
    # pl.subplot(2, 2, 1)
    # pl.imshow(im, 'gray')

    # pl.subplot(2, 2, 2)
    # pl.imshow(vis_textline0)
    # pltpath = filepath.replace("out", "plt")
    # pl.savefig(pltpath)
    # pl.show()

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

        if mubandict[x][0] < 0:
            mubandict[x][0] = 0
        if mubandict[x][1] < 0:
            mubandict[x][1] = 0

    mubandict = muban.de_muban(mubandict, 0.8)

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
