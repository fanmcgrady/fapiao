import copy
import os
import shutil

import cv2
import matplotlib.pyplot as pl

import fp
import lineToAttribute.getAtbt
from home.utils import Detect
from home.utils import detectType
from home.utils import flow
from home.utils import muban
from home.utils import PipeInvoice
from home.utils import FindCircle
from home.utils import xmlToDict


# 矫正 -> 行提取 -> ocr
def init(filename, type):
    # 矫正 -> 行提取
    out_file, flag, attributeLine = surface(filename, type)

    # ocr和分词
    jsonResult, origin = flow.cropToOcr(out_file, attributeLine, flag)
    return jsonResult, origin


def ocrWithoutSurface(out_file, line_result, flag=1):
    # ocr和分词
    jsonResult, origin = flow.cropToOcr(out_file, line_result, flag)
    return jsonResult, origin

# 矫正 -> 行提取
def surface(filename, type='blue'):
    filepath = os.path.join('allstatic', filename)

    isPipeTemplet = False
    # 原方法
    if type == None:
        midProcessResult = detectType.detectType('allstatic', filename)  # tangpeng 预处理
        # 未分类
    else:
        if type == 'blue' or type == 'excess':
            midProcessResult = PipeInvoice.getPipe('allstatic', filename, type, False)
        else:
            ##type == 'red'
            midProcessResult = [None, None, None]
            out_filename = filename.replace('upload', 'out')
            out_filename = os.path.join('allstatic', out_filename)

            # 拷贝到out
            shutil.copy(filepath, out_filename)

            midProcessResult[0] = out_filename
            midProcessResult[1] = 2  # 专票
            # 暂时用原图，不用校正后的图
            midProcessResult[2] = textline(midProcessResult[0])
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

    '''        'departCity': [29, 74, 218, 54],
            'arriveCity': [425, 68, 224, 64],
            'trainNumber': [230, 65, 203, 62],
            'invoiceDate': [0, 163, 357, 41],
            'seatNum': [392, 164, 203, 46],
            'idNum': [0, 343, 350, 45],
            'totalAmount': [3, 206, 212, 52],
            'ticketsNum': [34, 40, 202, 47]
        }'''
    redTemplet = {
        'idNum': [66, 242, 357, 38],
        'departCity': [66, 66, 222, 45],
        'arriveCity': [388, 66, 225, 47],
        'trainNumber': [288, 53, 103, 41],
        'invoiceDate': [66, 114, 237, 43],
        'seatNum': [400, 115, 210, 46],
        'totalAmount': [66, 163, 188, 34],
        'ticketsNum': [21, 23, 218, 47]
    }
    ''''''
    excessTemplet = {
        'departCity': [26, 40, 151, 33],
        'arriveCity': [271, 40, 169, 33],
        'trainNumber': [178, 35, 92, 32],
        'invoiceDate': [12, 82, 203, 29],
        'seatNum': [315, 79, 136, 33],
        'totalAmount': [12, 118, 167, 28],
        'ticketsNum': [23, 12, 147, 37]
    }

    # vatinvoice
    VATInvoiceTemplet = {
    }


    if midProcessResult[1] == 1:
        TemType = blueTemplet

    if midProcessResult[1] == 2:
        TemType = redTemplet

    if midProcessResult[1] == 3:
        TemType = excessTemplet

    if midProcessResult[1] == 11:  # 增值税专用             预留
        dic = xmlToDict.XmlTodict('VATInvoiceMuban.xml')

        tplt = [dic['QRCode'][0], dic['QRCode'][1], dic['figureX'][0] + dic['figureX'][2] / 2,
                dic['figureX'][1] + dic['figureX'][3] / 2]
        # print(tplt)
        for c in tplt:
            if c == None:
                print('Templet VATInvoice error')

        for item in dic:
            if item != 'QRCode' and item != 'figureX':
                # print(item)
                # tmp = MakeFileInV([[int(dic.get(item)[0]), int(dic.get(item)[1])], [int(dic.get(item)[2]), int(dic.get(item)[3])]], box, symbol, filePath, item, tplt)
                VATInvoiceTemplet[item] = [int(dic.get(item)[0]), int(dic.get(item)[1]), int(dic.get(item)[2]),
                                           int(dic.get(item)[3])]
        TemType = VATInvoiceTemplet

    rate = 1
    fcv = cv2.imread(filepath, 1)
    w1 = fcv.shape
    if w1[0] + w1[1] > 1500:
        rate = 0.5
        # print("rate : 0.5")

    if midProcessResult[1] == 1:
        if isPipeTemplet:
            Templet = midProcessResult[3]
            print('inPipeTem')
        else:
            box = Detect.detect(cv2.imread(midProcessResult[0]), rate)
            Templet = adjustToTextLine(TemType, box, midProcessResult[1], None)  # 蓝火车票
    if midProcessResult[1] == 2:
        rate = 2.0
        print("rate : 2.0")
        box = Detect.detect(cv2.imread(midProcessResult[0]), rate)
        # print( box.tolist())
        Templet = adjustToTextLine(TemType, box, midProcessResult[1], None)  # 红火车票
    if midProcessResult[1] == 3:
        if isPipeTemplet:
            Templet = midProcessResult[3]
        else:
            rate = 1.0
            print("rate : 1.0")
            box = Detect.detect(cv2.imread(midProcessResult[0]), rate)
            # print( box.tolist())
            Templet = adjustToTextLine(TemType, box, midProcessResult[1], None)  # 红(补票)车票
    if midProcessResult[1] == 11:
        box = Detect.detect(cv2.imread(midProcessResult[0]), rate)
        figureP = FindCircle.findSymbol(filepath)
        StBox = sortBox(box)
        Templet = adjustToTextLine(TemType, [StBox[0], StBox[1], figureP[0], figureP[1]], midProcessResult[1],
                                   tplt)  # 增值税专票

    attributeLine = lineToAttribute.getAtbt.compute(midProcessResult[2], Templet)

    # 生成行提取的图片
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
    show_textline = False
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

    if show_textline:
        # 绘制结果
        vis_textline0 = fp.util.visualize.rects(im, rects)
        # vis_textline1 = fp.util.visualize.rects(im, rects, types)
        # 显示
        pl.figure(figsize=(15, 10))
        pl.subplot(2, 2, 1)
        pl.imshow(im, 'gray')

        pl.subplot(2, 2, 2)
        pl.imshow(vis_textline0)
        pl.show()

    return rects


def adjustToTextLine(mubandict, box, typeT, templet):  # box顺序需要调整

    # 检查二维码错误定位的长宽比
    StandardRate = 0.7

    if typeT != 11:
        midbox = sortBox(box)

        # 长宽检测二维码
        rateHtoW = (midbox[3] - midbox[1]) / (midbox[2] - midbox[0])
        if rateHtoW > 1.0 / StandardRate or rateHtoW < StandardRate:
            print('QRCode seems wrong')
    else:
        midbox = box
        rateHtoW = (midbox[3] - midbox[1]) / (midbox[2] - midbox[0])
        if rateHtoW > 1.0 / StandardRate or rateHtoW < StandardRate:
            print('QRCode seems wrong')
    #print(midbox)

    mubanBox = []
    if typeT == 1:
        mubanBox = [526, 272, 634, 379]  # [x1,y1,x2,y2]
    if typeT == 2:
        # mubanBox = [483, 259, 632, 439]
        # mubanBox = [365, 234, 425, 297]#[[365, 297], [365, 234], [425, 234], [425, 297]]
        # [[601, 409], [507, 408], [508, 318], [602, 319]]
        mubanBox = [508, 318, 601, 409]  # use TR009.JPG
    if typeT == 3:
        mubanBox = [365, 234, 425, 297]  # [[365, 297], [365, 234], [425, 234], [425, 297]]补票
    if typeT == 11:
        mubanBox = templet

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

    if typeT == 1:
        # 调整蓝票框
        mubandict = muban.de_muban(mubandict, 0.8)
    if typeT == 11:
        mubandict = muban.de_muban(mubandict, 0.9)

    return mubandict


def sortBox(box):
    # box[[536, 387], [534, 280], [641, 279], [643, 386]]
    a = []
    b = []
    for x in box:
        a.append(x[0])
        b.append(x[1])

    return [min(a), min(b), max(a), max(b)]


'''dset_dir = 'E:/DevelopT/pycharm_workspace/Ocr/Image'
jpgs = fp.util.path.files_in_dir(dset_dir, '.png')
print(jpgs[9])
'''
# init('TR009.jpg','red')

'''xl = textline('Image_065_turned.jpeg')
print(xl)
print(type(xl))
'''
