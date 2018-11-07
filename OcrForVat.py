import sys
sys.path.append("ocr")

import copy

import cv2
import matplotlib.pyplot as pl
from PIL import Image

import FindCircle
import flow
from home import views

if not views.local_start:
    from scanQRCode.scan_qrcode import recog_qrcode, recog_qrcode_ex
import json
import os
import numpy as np
import SemanticCorrect.posteriorCrt
import fp
import InterfaceType
import lineToAttribute.getAtbt
import xmlToDict
import FindCircle
import flow
import muban

from TicToc import Timer


def jwkj_get_filePath_fileName_fileExt(filename):  # 提取路径
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


import connecter


def newOcr(filepath):
    return connecter.OCR(filepath)


def decWidth(array, axis):
    array[0] = array[0] + axis * array[2]
    array[2] = (1 - axis) * array[2]

    return array


def CropPic(filePath, recT, typeT, origin_filePath, debug=False, isusebaidu=False):
    ocrResult = {}
    img = Image.open(filePath)
    # img = cv2.imread(filePath, 1)

    # 确认目录
    # if os.path.exists(
    #         jwkj_get_filePath_fileName_fileExt(filePath)[0] + "./tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
    #             1]) == False:
    #     os.mkdir(
    #         jwkj_get_filePath_fileName_fileExt(filePath)[0] + "./tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
    #             1])

    # 加载自识别ocr模型（增值税专票模型）可设置typeT为11加载

    for x in recT:
        sp = img.crop((recT[x][0], recT[x][1], recT[x][0] + recT[x][2], recT[x][1] + recT[x][3]))
        # sp = img[int(recT[x][1]): int(recT[x][1] + recT[x][3]), int(recT[x][0]):int(recT[x][0] + recT[x][2])]
        sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + '/' + jwkj_get_filePath_fileName_fileExt(filePath)[
            1] + "_" + x + ".jpg"
        # cv2.imwrite(sFPN, sp)
        sp.save(sFPN)
        # print(x +"  : "+sFPN)

        if debug == False:
            # if (x != 'invoiceNo'):
            # # 测试如此识别并不能修正字体不能识别的问题
            if isusebaidu:
                midResult = flow.OcrPic(sFPN)
            else:
                midResult = newOcr(sFPN)
            # else:
            #     midResult = OcrNoPic(sFPN)

            print(midResult + '   isUseBaidu: ' + str(isusebaidu))
            ocrResult[x] = midResult

    print(ocrResult)
    pC = SemanticCorrect.posteriorCrt.posteriorCrt()

    print("origin_filePath " + origin_filePath)
    if typeT == 11 and debug == False:
        if ocrResult['invoiceDate'][:4] == '开票日期' or len(ocrResult['invoiceDate']) < 4:

            # 返回上级
            imgl = Image.open(origin_filePath)
            recT['invoiceDate'] = mubanDetectInvoiceDate(origin_filePath)['invoiceDate']
            if recT['invoiceDate'] != None:
                sp = imgl.crop((recT['invoiceDate'][0], recT['invoiceDate'][1],
                                recT['invoiceDate'][0] + recT['invoiceDate'][2],
                                recT['invoiceDate'][1] + recT['invoiceDate'][3]))

                sFPN = jwkj_get_filePath_fileName_fileExt(origin_filePath)[0] + "/tmp/" + \
                       jwkj_get_filePath_fileName_fileExt(origin_filePath)[1] + "/" + \
                       jwkj_get_filePath_fileName_fileExt(origin_filePath)[
                           1] + "_" + 'invoiceDateFix' + ".jpg"
                sp.save(sFPN)

                if isusebaidu:
                    midResult = flow.OcrPic(sFPN)
                else:
                    midResult = newOcr(sFPN)
                # midResult = flow.OcrPic(sFPN)

                print('invoiceDateFix: ' + midResult)
                ocrResult['invoiceDate'] = midResult
            else:
                print("find Circle error!")

    js = InterfaceType.JsonInterface.invoice()
    if typeT == 11:
        pC.setVATParaFromVATDict(ocrResult)
        pC.startVATCrt()
        js.setValueWithDict(pC.VATdic)
        jsoni = js.dic

    else:
        pC.setTrainTicketParaFromDict(ocrResult)
        pC.startTrainTicketCrt()
        js.setValueWithDict(pC.dic)
        jsoni = js.dic

    return json.dumps(jsoni).encode().decode("unicode-escape")


def newMubanDetect(filepath, type='special', pars=dict(textline_method='simple'), timer=None):
    print(type)
    print(pars)

    # 'elec'：增值税电子发票
    # 'special'：增值税专用发票
    # 'normal'：增值税普通发票
    # pars = dict(textline_method='textboxes')  # 使用 深度学习 方法，目前用的CPU，较慢 ?
    # pars = dict(textline_method='simple')  # 使用 深度学习 方法，目前用的CPU，较慢 ?

    pipe = fp.vat_invoice.pipeline.VatInvoicePipeline(type, pars=pars, debug=False)  # 请用debug=False
    # pipe = fp.vat_invoice.pipeline.VatInvoicePipeline('special', debug=False) # 请用False
    im = cv2.imread(filepath, 1)
    im = cv2.resize(im, None, fx=0.5, fy=0.5)

    pipe(im)
    timer.toc(content="行提取")

    # pl.figure(figsize=(12, 12))
    # pl.imshow(pipe.debug['result'])
    # pl.show()
    attributeLine = {}

    if type == 'special' or type == 'normal':

        if pipe.predict('tax_free_money') is None:
            attributeLine = {
                'invoiceCode': list(pipe.predict('type')),
                'invoiceNo': list(pipe.predict('serial')),
                # 'invoiceDate': list(pipe.predict('time')),
                # 'invoiceAmount': list(pipe.predict('tax_free_money'))
            } if pipe.predict('time') is None else {
                'invoiceCode': list(pipe.predict('type')),
                'invoiceNo': list(pipe.predict('serial')),
                'invoiceDate': list(pipe.predict('time')),
                # 'invoiceAmount': list(pipe.predict('tax_free_money'))
            }

        else:
            attributeLine = {
                'invoiceCode': list(pipe.predict('type')),
                'invoiceNo': list(pipe.predict('serial')),
                # 'invoiceDate': list(pipe.predict('time')),
                'invoiceAmount': list(pipe.predict('tax_free_money'))
            } if pipe.predict('time') is None else {
                'invoiceCode': list(pipe.predict('type')),
                'invoiceNo': list(pipe.predict('serial')),
                'invoiceDate': list(pipe.predict('time')),
                'invoiceAmount': list(pipe.predict('tax_free_money'))
            }
    elif type == 'elec':
        attributeLine = {
            'invoiceCode': list(pipe.predict('type')),
            'invoiceNo': list(pipe.predict('serial')),
            'invoiceAmount': list(pipe.predict('tax_free_money')),
            'verifyCode': list(pipe.predict('verify'))
        } if pipe.predict('time') is None else {
            'invoiceCode': list(pipe.predict('type')),
            'invoiceNo': list(pipe.predict('serial')),
            'invoiceDate': list(pipe.predict('time')),
            'invoiceAmount': list(pipe.predict('tax_free_money')),
            'verifyCode': list(pipe.predict('verify'))
        }
    else:
        print('type input error !')

    for c in attributeLine:
        attributeLine[c][0] = attributeLine[c][0] - 0.02 * attributeLine[c][2]
        attributeLine[c][1] = attributeLine[c][1] - 0.2 * attributeLine[c][3]
        attributeLine[c][2] = attributeLine[c][2] * 1.04
        attributeLine[c][3] = attributeLine[c][3] * 1.4
        if attributeLine[c][0] < 0:
            attributeLine[c][0] = 0
        if attributeLine[c][1] < 0:
            attributeLine[c][1] = 0

    if type == 'elec':
        attributeLine['invoiceCode'] = decWidth(attributeLine['invoiceCode'], float(86.0 / 220.0))
        attributeLine['invoiceNo'] = decWidth(attributeLine['invoiceNo'], float(88.0 / 178.0))
        if 'invoiceDate' in attributeLine.keys():
            attributeLine['invoiceDate'] = decWidth(attributeLine['invoiceDate'], float(86.0 / 221.0))
        attributeLine['verifyCode'] = decWidth(attributeLine['verifyCode'], float(90.0 / 324.0))

    print(attributeLine)
    timer.toc(content="行提取矫正")

    # 新建目录tmp
    if os.path.exists(jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp") == False:
        os.mkdir(jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp")

    # 新建目录tmp/'filename'/
    if os.path.exists(
            jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp/" +
            jwkj_get_filePath_fileName_fileExt(filepath)[
                1]) == False:
        os.mkdir(
            jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp/" +
            jwkj_get_filePath_fileName_fileExt(filepath)[
                1])

    # img = Image.open(filepath)
    # 如为simple方法 先存储pipe。surface_image为初始图（后续识别定位基于该图）
    # if pars == dict(textline_method='simple'):

    # print(jwkj_get_filePath_fileName_fileExt(filepath)[1])
    #
    # print(surfaceImagePath)

    surfaceImagePath = jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp/" + \
                       jwkj_get_filePath_fileName_fileExt(filepath)[1] + "/origin.jpg"
    cv2.imwrite(surfaceImagePath, pipe.surface_image)

    filepathS = surfaceImagePath
    img = Image.open(filepathS)  # 若为simple 方法 调用pipe后的图为初始图

    # 二值化
    im = img.convert('L')
    img = np.array(im)
    h, w = img.shape

    # 是否采用自适应二值化方法
    # isAdoptive = False
    if type == 'elec':
        isAdoptive = False  # 测试中
    else:
        isAdoptive = True  # 测试中

    thresholding = 160

    if isAdoptive:
        # 自适应二值化
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)
    else:
        # 手动二值化
        for i in range(h):
            for j in range(w):
                if img[i, j] > thresholding:
                    img[i, j] = 255
                else:
                    img[i, j] = 0

    # 二值化图路径

    binaryzationSurfaceImagePath = jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp/" + \
                                   jwkj_get_filePath_fileName_fileExt(filepath)[1] + "/binaryzationSurfaceImage.jpg"

    # print(binaryzationSurfaceImagePath+"    :binaryzationSurfaceImagePath")
    cv2.imwrite(binaryzationSurfaceImagePath, np.array(img))
    # print(binaryzationSurfaceImagePath + "2    :over")

    # 生成行提取的图片
    plt_rects = []
    for x in attributeLine:
        plt_rects.append(attributeLine[x])
    # 显示
    vis_textline0 = fp.util.visualize.rects(cv2.imread(binaryzationSurfaceImagePath, 0), plt_rects)
    pl.imshow(vis_textline0)
    # 保存到line目录
    try:
        pltpath = filepath.replace("upload", "line")
        pl.savefig(pltpath)
    except:
        pass
    timer.toc(content="行提取图绘制")

    jsonResult = CropPic(binaryzationSurfaceImagePath, attributeLine, 11, filepath, debug=False,
                         isusebaidu=False)  # ocr和分词
    timer.toc(content="切图ocr识别")
    print(jsonResult)

    return jsonResult, timer


def mubanDetectInvoiceDate(filepath, setKey='invoiceDate'):
    midProcessResult = [None, None]
    midProcessResult[0] = filepath
    midProcessResult[1] = 11
    # vat发票专票
    VATInvoiceTemplet = {
    }

    dic = xmlToDict.XmlTodict('ocr/VATInvoiceSimpleMuban.xml')

    # tplt = [dic['QRCode'][0], dic['QRCode'][1], dic['figureX'][0] + dic['figureX'][2] / 2, dic['figureX'][1] + dic['figureX'][3] / 2]
    tplt = [dic['figureX'][0] + dic['figureX'][2] / 2, dic['figureX'][1] + dic['figureX'][3] / 2]
    # print(tplt)
    '''
    for c in tplt:
        if c == None:
            print('Templet VATInvoice error')
    '''
    TemType = {}
    if midProcessResult[1] == 11:  # 增值税专用
        VATInvoiceTemplet[setKey] = [int(dic.get(setKey)[0]), int(dic.get(setKey)[1]), int(dic.get(setKey)[2]),
                                     int(dic.get(setKey)[3])]
        TemType = VATInvoiceTemplet

    fcv = cv2.imread(filepath, 1)
    # print(fcv)
    try:
        w1 = fcv.shape
    except:
        print("picture is None")

    if w1[0] + w1[1] > 1500:
        rate = 0.5
        # print("rate : 0.5")

    if midProcessResult[1] == 11:
        # box = Detect.detect(cv2.imread(midProcessResult[0]), rate)
        figureP = FindCircle.findSymbol(filepath)
        # StBox = sortBox(box)
        # print(box)
        # print(figureP)
        # print(StBox)
        if figureP == None:
            return None
        Templet = simplyAdjust(TemType, [figureP[0], figureP[1]], tplt, w1)  # 增值税专票

        attributeLine = lineToAttribute.getAtbt.compute(textline(midProcessResult[0]), Templet)

        # 生成行提取的图片
        plt_rects = []
        for x in attributeLine:
            plt_rects.append(attributeLine[x])
        # 显示
        vis_textline0 = fp.util.visualize.rects(cv2.imread(midProcessResult[0], 0), plt_rects)
        pl.imshow(vis_textline0)
        # 保存到line目录
        pltpath = midProcessResult[0].replace("upload", "line")
        pl.savefig(pltpath)

    return attributeLine


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

    if typeT != 11:
        midbox = sortBox(box)
    else:
        midbox = box
    # print(midbox)

    mubanBox = []
    if typeT == 1:
        mubanBox = [526, 272, 634, 379]  # [x1,y1,x2,y2]
    if typeT == 2:
        # mubanBox = [483, 259, 632, 439]
        # mubanBox = [365, 234, 425, 297]#[[365, 297], [365, 234], [425, 234], [425, 297]]
        # [[601, 409], [507, 408], [508, 318], [602, 319]]
        mubanBox = [508, 318, 601, 409]  # use TR009.JPG
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

    # print(mubandict)

    if typeT == 1:
        # 调整蓝票框
        mubandict = muban.de_muban(mubandict, 0.8)
    if typeT == 11:
        mubandict = muban.de_muban(mubandict, 0.9)

    return mubandict


def simplyAdjust(mubandict, box, tplt, shape):
    for x in mubandict:
        mubandict[x][0] = mubandict[x][0] + box[0] - tplt[0]
        mubandict[x][1] = mubandict[x][1] + box[1] - tplt[1]
    if mubandict[x][0] < 0:
        mubandict[x][0] = 0
    if mubandict[x][1] < 0:
        mubandict[x][1] = 0
    if mubandict[x][0] + mubandict[x][2] > shape[1]:
        mubandict[x][0] = shape[1] - mubandict[x][2]
    if mubandict[x][1] + mubandict[x][3] > shape[0]:
        mubandict[x][1] = shape[0] - mubandict[x][3]
    # print(mubandict)

    mubandict = muban.de_muban(mubandict, 1.0)
    return mubandict


def sortBox(box):
    # box[[536, 387], [534, 280], [641, 279], [643, 386]]
    a = []
    b = []
    for x in box:
        a.append(x[0])
        b.append(x[1])

    return [min(a), min(b), max(a), max(b)]


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


def init(filepath, type='special', pars=dict(textline_method='textboxes')):
# def init(filepath, type='special', pars=dict(textline_method='simple')):
    '''
    mage = cv2.imread(filepath,0)
    str_info, position = recog_qrcode(image, roi=None)

    #二维码无法识别
    if str_info == None:
    '''
    timer = Timer()
    timer.tic()

    if not views.local_start:
        res = scanQRc(filepath)
        timer.toc(content="二维码识别")

        if res[0] != '':
            # 显示二维码
            plt_rects = []
            plt_rects.append(
                [res[1][1][0],
                 res[1][1][1],
                 res[1][3][0] - res[1][0][0],
                 res[1][0][1] - res[1][1][1]])
            # 显示
            vis_textline0 = fp.util.visualize.rects(cv2.imread(filepath, 0), plt_rects)
            # 运行代码需要如下部分
            pl.imshow(vis_textline0)
            # 保存到line目录
            pltpath = filepath.replace("upload", "line")
            pl.savefig(pltpath)

            resArray = getArrayFromStr(res[0])
            js = InterfaceType.JsonInterface.invoice()
            js.setVATInvoiceFromArray(resArray)

            jsoni = js.dic
            print(jsoni)
            return json.dumps(jsoni).encode().decode("unicode-escape"), timer
        else:
            return newMubanDetect(filepath, type, pars, timer)
    else:
        # print('newMubanD')
        return newMubanDetect(filepath, type, pars, timer)
    '''
    else:
        js = InterfaceType.JsonInterface.invoice()
        js.setInfo(str_info)
        jsoni = js.dic

        return json.dumps(jsoni).encode().decode("unicode-escape")
    '''


'''dset_dir = 'E:/DevelopT/pycharm_workspace/Ocr/Image'
jpgs = fp.util.path.files_in_dir(dset_dir, '.png')
print(jpgs[9])
'''

if __name__ == '__main__':
    # dset = '/home/huangzheng/ocr/testPic/3/'
    # jpgs = fp.util.path.files_in_dir(dset, '.jpg')
    # for c in jpgs:
    #     print(c)
    #     # dset = 'D:/Development/data/2/'
    #     # c = 'Image_00147.jpg'
    #     init(os.path.join(dset, c), type='special', pars=dict(textline_method='textboxes'))
    #     print('__________________________  ' + c + '  _______________________')

    print("in")
    init('/home/huangzheng/ocr/testPic/3/Image_00006.jpg', type='special', pars=dict(textline_method='textboxes'))
    # init('Image_00164.jpg', type='normal', pars=dict(textline_method='simple'))
    # init('Image_00131.jpg', type='elec', pars=dict(textline_method='simple'))
