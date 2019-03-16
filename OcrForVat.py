import copy

import OCR
import cv2
import matplotlib.pyplot as pl
from PIL import Image

from connector import FindCircle, flow, connecter
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
import muban

from connector.TicToc import Timer
import time


def jwkj_get_filePath_fileName_fileExt(filename):  # 提取路径
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def newOcr(filepath, typeP, x):
    return connecter.OCR(filepath, typeP, x)


def decWidth(array, axis):
    array[0] = array[0] + axis * array[2]
    array[2] = (1 - axis) * array[2]

    return array


def CropPic(filePath, recT, typeT, origin_filePath, pars, typeP, debug=False, isusebaidu=False):
    ocrResult = {}

    # 二值化
    time1 = time.time()

    img = Image.open(filePath)
    # img = cv2.imread(filePath, 1)

    # 确认目录
    # if os.path.exists(
    #         jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
    #             1]) == False:
    #     os.mkdir(
    #         jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
    #             1])

    # -----------------------------------------------------------二值化---------------------
    isAdoptive = True
    imgL = Image.open(filePath)  # 若为simple 方法 调用pipe后的图为初始图

    # 二值化
    imL = imgL.convert('L')
    imgL = np.array(imL)
    h, w = imgL.shape

    # 是否采用自适应二值化方法
    isAdoptive = False
    if typeP != 'elec':  # 测试中
        hist, _ = np.histogram(imgL, bins=[0, 50, 100, 150, 200, 255])
        all = imgL.shape[0] * imgL.shape[1]
        t = hist[0] + hist[-1]
        if t / all < 0.95:
            isAdoptive = True  # 测试中

    # isAdoptive = False
    thresholding = 160
    timex = time.time()
    print("判断   " + str(timex - time1))

    print("isAdoptive:  " + str(isAdoptive))
    if isAdoptive:
        # 自适应二值化
        imgL = cv2.adaptiveThreshold(imgL, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)
    # else:
    #     # 手动二值化
    #     for i in range(h):
    #         for j in range(w):
    #             if imgL[i, j] > thresholding:
    #                 imgL[i, j] = 255
    #             else:
    #                 imgL[i, j] = 0

    # 二值化图路径

    binaryzationSurfaceImagePath = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/binaryzationSurfaceImage.jpg"

    cv2.imwrite(binaryzationSurfaceImagePath, np.array(imgL))

    imgL = Image.open(binaryzationSurfaceImagePath)

    # ----------------------------------------------------二值化 ---------------------------------

    # 裁剪（校验码处理）
    time2 = time.time()

    print('二值化过程:   ' + str(time2 - time1))

    # 校验码处理
    threshold = fp.core.thresh.HybridThreshold(rows=1, cols=4, local='gauss')

    for x in recT:

        if typeP == 'elec':  # 电票

            sp = img.crop((recT[x][0], recT[x][1], recT[x][0] + recT[x][2], recT[x][1] + recT[x][3]))

            w, h = sp.size

            if w / h * 32 > 512:
                w = int(512 / 32 * h) - 1
                sp = img.crop((recT[x][0], recT[x][1], recT[x][0] + w, recT[x][1] + h))
        else:

            if x == 'verifyCode':
                if len(recT[x]) == 2:
                    sp1 = imgL.crop(
                        (recT[x][0][0], recT[x][0][1], recT[x][0][0] + recT[x][0][2], recT[x][0][1] + recT[x][0][3]))
                    sp2 = imgL.crop(
                        (recT[x][1][0], recT[x][1][1], recT[x][1][0] + recT[x][1][2], recT[x][1][1] + recT[x][1][3]))
                else:
                    sp = imgL.crop((recT[x][0], recT[x][1], recT[x][0] + recT[x][2], recT[x][1] + recT[x][3]))

            elif x == 'invoiceNo':
                sp = img.crop((recT[x][0], recT[x][1], recT[x][0] + recT[x][2], recT[x][1] + recT[x][3]))
            else:
                sp = imgL.crop((recT[x][0], recT[x][1], recT[x][0] + recT[x][2], recT[x][1] + recT[x][3]))
        if recT[x][0] == 0 and recT[x][1] == 0 and recT[x][2] == 0 and recT[x][3] == 0:
            print("↑--------↑--------↑--------↑ recT : " + x + " is error↑--------↑--------↑")

            continue
        # sp = img[int(recT[x][1]): int(recT[x][1] + recT[x][3]), int(recT[x][0]):int(recT[x][0] + recT[x][2])]

        if x == 'verifyCode' and len(recT[x]) == 2:
            # if len(recT[x]) == 2:#存图  verifyCode例外（多图）
            sFPN1 = jwkj_get_filePath_fileName_fileExt(filePath)[0] + '/' + \
                    jwkj_get_filePath_fileName_fileExt(filePath)[
                        1] + "_" + x + "_1.jpg"
            sFPN2 = jwkj_get_filePath_fileName_fileExt(filePath)[0] + '/' + \
                    jwkj_get_filePath_fileName_fileExt(filePath)[
                        1] + "_" + x + "_2.jpg"

            sp1.save(sFPN1)
            sp2.save(sFPN2)

            imcv1 = cv2.imread(sFPN1, 1)[:, :, 2]
            imcv2 = cv2.imread(sFPN2, 1)[:, :, 2]
            bi_im1 = threshold(imcv1)
            bi_im2 = threshold(imcv2)
            cv2.imwrite(sFPN1, bi_im1)
            cv2.imwrite(sFPN2, bi_im2)

            print('--------------  ---------------' + sFPN1)
            print('--------------  ---------------' + sFPN2)
        else:
            sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + '/' + jwkj_get_filePath_fileName_fileExt(filePath)[
                1] + "_" + x + ".jpg"
            print('--------------  ---------------' + sFPN)
            # cv2.imwrite(sFPN, sp)
            sp.save(sFPN)
            if typeP == 'normal' and x == 'verifyCode':
                imcv = cv2.imread(sFPN, 1)[:, :, 2]
                bi_im = threshold(imcv)
                cv2.imwrite(sFPN, bi_im)
        # print(x +"  : "+sFPN)
        if pars == dict(textline_method='simple') and x == 'invoiceNo' and (typeP == 'special' or typeP == 'normal'):
            OCR.utils.convert(sFPN)
        if debug == False:
            # if (x != 'invoiceNo'):
            # # 测试如此识别并不能修正字体不能识别的问题
            midResult = ''
            if isusebaidu:
                midResult = ''
                if x == 'verifyCode' and len(recT[x]) == 2:
                    # if len(recT[x]) == 2:
                    midResult1 = flow.OcrPic(sFPN1)
                    midResult2 = flow.OcrPic(sFPN2)
                    midResult += midResult2 if len(midResult2) > 19 else ''
                    midResult += midResult1 if len(midResult1) > 19 else ''
                else:
                    if x == 'verifyCode':
                        # 校验码
                        mdrs = flow.OcrPic(sFPN)
                        midResult = mdrs if len(mdrs) > 19 else ''
                    else:
                        midResult = flow.OcrPic(sFPN)
            else:
                midResult = ''
                if x == 'verifyCode' and len(recT[x]) == 2:
                    # if len(recT[x]) == 2:
                    midResult1 = newOcr(sFPN1, typeP, x)
                    midResult2 = newOcr(sFPN2, typeP, x)
                    midResult += midResult2 if len(midResult2) > 19 else ''
                    midResult += midResult1 if len(midResult1) > 19 else ''
                else:
                    if x == 'verifyCode':
                        # 校验码
                        mdrs = newOcr(sFPN, typeP, x)
                        midResult = mdrs if len(mdrs) > 19 else ''
                    elif typeP == 'elec' and x == 'invoiceAmount':
                        midResult = newOcr(sFPN, 'normal', x)
                    elif typeP == 'elec':
                        midResult = newOcr(sFPN, typeP, x)
                    else:
                        midResult = newOcr(sFPN, typeP, x)

            # else:
            #     midResult = OcrNoPic(sFPN)

            print(midResult + '   isUseBaidu: ' + str(isusebaidu))
            ocrResult[x] = midResult

    # 后矫正
    time6 = time.time()
    print('切图识别：    ' + str(time6 - time2))

    print(ocrResult)
    pC = SemanticCorrect.posteriorCrt.posteriorCrt()

    print("origin_filePath " + origin_filePath)
    # if typeT == 11 and debug == False:
    #     if ocrResult['invoiceDate'][:4] == '开票日期' or len(ocrResult['invoiceDate']) < 4:
    #
    #         # 返回上级
    #         imgl = Image.open(origin_filePath)
    #         recT['invoiceDate'] = mubanDetectInvoiceDate(origin_filePath)['invoiceDate']
    #         if recT['invoiceDate'] != None:
    #             sp = imgl.crop((recT['invoiceDate'][0], recT['invoiceDate'][1],
    #                             recT['invoiceDate'][0] + recT['invoiceDate'][2],
    #                             recT['invoiceDate'][1] + recT['invoiceDate'][3]))
    #
    #             sFPN = jwkj_get_filePath_fileName_fileExt(origin_filePath)[0] + "/tmp/" + \
    #                    jwkj_get_filePath_fileName_fileExt(origin_filePath)[1] + "/" + \
    #                    jwkj_get_filePath_fileName_fileExt(origin_filePath)[
    #                        1] + "_" + 'invoiceDateFix' + ".jpg"
    #             sp.save(sFPN)
    #
    #             if isusebaidu:
    #                 midResult = flow.OcrPic(sFPN)
    #             else:
    #                 midResult = newOcr(sFPN, typeP)
    #             # midResult = flow.OcrPic(sFPN)
    #
    #             print('invoiceDateFix: ' + midResult)
    #             ocrResult['invoiceDate'] = midResult
    #         else:
    #             print("find Circle error!")

    js = InterfaceType.JsonInterface.invoice()
    if typeT == 11:
        pC.setVATParaFromVATDict(ocrResult)
        if (typeP == 'normal' or typeP == 'special') and ('invoiceNoS' in pC.VATdic.keys()):
            tms = pC.VATdic['invoiceNoS']
            pC.VATdic['invoiceNoS'] = pC.VATdic['invoiceNo']
            pC.VATdic['invoiceNo'] = tms
            print('Use  invoiceNoS ---------------------------------')
        if typeP != 'elec':
            pC.startVATCrt()
        else:
            pC.startElecVATCrt()
        js.setValueWithDict(pC.VATdic)
        jsoni = js.dic

    else:
        pC.setTrainTicketParaFromDict(ocrResult)
        pC.startTrainTicketCrt()
        js.setValueWithDict(pC.dic)
        jsoni = js.dic

    time7 = time.time()
    print('后矫正： ' + str(time7 - time6))

    return json.dumps(jsoni).encode().decode("unicode-escape")


def newMubanDetect(filepath, typeP='special', pars=dict(textline_method='simple'), timer=None):
    print(typeP)
    print(pars)

    # 'elec'：增值税电子发票
    # 'special'：增值税专用发票
    # 'normal'：增值税普通发票
    # pars = dict(textline_method='textboxes')  # 使用 深度学习 方法，目前用的CPU，较慢 ?
    # pars = dict(textline_method='simple')  # 使用 深度学习 方法，目前用的CPU，较慢 ?

    pipe = fp.vat_invoice.pipeline.VatInvoicePipeline(typeP, pars=pars, debug=False)  # 请用debug=False
    # pipe = fp.vat_invoice.pipeline.VatInvoicePipeline('special', debug=False) # 请用False
    im = cv2.imread(filepath, 1)
    # im = cv2.resize(im, None, fx=0.5, fy=0.5)
    pipe(im)

    timer.toc(content="行提取")
    # pl.figure(figsize=(12, 12))
    # pl.imshow(pipe.debug['result'])
    # pl.show()
    attributeLine = {}

    # atbArray = ['type', 'serial', 'time', 'tax_free_money', 'serial_tiny', 'verify']
    atbDic = {
        'type': 'invoiceCode',
        'serial': 'invoiceNo',
        'time': 'invoiceDate',
        'tax_free_money': 'invoiceAmount',
        'serial_tiny': 'invoiceNoS',
        'verify': 'verifyCode'}

    # if typeP == 'special' or :
    # print('type'+'  '+str(pipe.predict('type')))
    # print('invoiceNo'+'  '+str(pipe.predict('serial')))
    # print('invoiceDate'+'  '+str(pipe.predict('time')))
    # print('invoiceAmount'+'  '+str(pipe.predict('tax_free_money')))
    # print('invoiceNoS'+'  ')
    # print(str(pipe.predict('serial_tiny')))

    for atb in atbDic.keys():
        if not pipe.predict(atb) is None:
            #  print(atb+'  '+str(pipe.predict(atb)))
            attributeLine[atbDic[atb]] = list(pipe.predict(atb))

    #     if pipe.predict('tax_free_money') is None:
    #         attributeLine = {
    #             'invoiceCode': list(pipe.predict('type')),
    #             'invoiceNo': list(pipe.predict('serial')),
    #             # 'invoiceDate': list(pipe.predict('time')),
    #             # 'invoiceAmount': list(pipe.predict('tax_free_money'))
    #         } if pipe.predict('time') is None else {
    #             'invoiceCode': list(pipe.predict('type')),
    #             'invoiceNo': list(pipe.predict('serial')),
    #             'invoiceDate': list(pipe.predict('time')),
    #             # 'invoiceAmount': list(pipe.predict('tax_free_money'))
    #         }
    #
    #     else:
    #         attributeLine = {
    #             'invoiceCode': list(pipe.predict('type')),
    #             'invoiceNo': list(pipe.predict('serial')),
    #             # 'invoiceDate': list(pipe.predict('time')),
    #             'invoiceAmount': list(pipe.predict('tax_free_money'))
    #         } if pipe.predict('time') is None else {
    #             'invoiceCode': list(pipe.predict('type')),
    #             'invoiceNo': list(pipe.predict('serial')),
    #             'invoiceDate': list(pipe.predict('time')),
    #             'invoiceAmount': list(pipe.predict('tax_free_money'))
    #         }
    # elif typeP == 'normal' or typeP == 'elec':
    #     if pipe.predict('tax_free_money') is None:
    #         attributeLine = {
    #             'invoiceCode': list(pipe.predict('type')),
    #             'invoiceNo': list(pipe.predict('serial')),
    #             # 'invoiceAmount': list(pipe.predict('tax_free_money')),
    #             'verifyCode': list(pipe.predict('verify'))
    #         } if pipe.predict('time') is None else {
    #             'invoiceCode': list(pipe.predict('type')),
    #             'invoiceNo': list(pipe.predict('serial')),
    #             'invoiceDate': list(pipe.predict('time')),
    #             # 'invoiceAmount': list(pipe.predict('tax_free_money')),
    #             'verifyCode': list(pipe.predict('verify'))
    #         }
    #
    #     else:
    #         attributeLine = {
    #             'invoiceCode': list(pipe.predict('type')),
    #             'invoiceNo': list(pipe.predict('serial')),
    #             'invoiceAmount': list(pipe.predict('tax_free_money')),
    #             'verifyCode': list(pipe.predict('verify'))
    #         } if pipe.predict('time') is None else {
    #             'invoiceCode': list(pipe.predict('type')),
    #             'invoiceNo': list(pipe.predict('serial')),
    #             'invoiceDate': list(pipe.predict('time')),
    #             'invoiceAmount': list(pipe.predict('tax_free_money')),
    #             'verifyCode': list(pipe.predict('verify'))
    #         }
    # else:
    #     print('type input error !')

    # 设置框区缩放倍数
    if pars == dict(textline_method='simple'):
        wAxis = 0.04
        hAxis = 0.1

    elif pars == dict(textline_method='textboxes'):
        wAxis = 0.02
        hAxis = 0.1
    for c in attributeLine:
        # print(attributeLine[c])
        if typeP == 'special' and pars == dict(textline_method='textboxes') and c in ['invoiceNo', 'invoiceAmount']:
            continue

        attributeLine[c][0] = np.array(attributeLine[c][0]).tolist()

        if type(attributeLine[c][0]) == type([1, 2, 3]):

            for ind, b in enumerate(attributeLine[c]):
                # print(ind)
                if ind != 0:
                    attributeLine[c][ind] = np.array(attributeLine[c][ind]).tolist()
                continue
                # print(attributeLine[c][ind])
                attributeLine[c][ind][0] = attributeLine[c][ind][0] - wAxis * attributeLine[c][ind][2]
                attributeLine[c][ind][1] = attributeLine[c][ind][1] - hAxis * attributeLine[c][ind][3]
                attributeLine[c][ind][2] = attributeLine[c][ind][2] * (1 + 2 * wAxis)
                attributeLine[c][ind][3] = attributeLine[c][ind][3] * (1 + 2 * hAxis)
                if attributeLine[c][ind][0] < 0:
                    attributeLine[c][ind][0] = 0
                if attributeLine[c][ind][1] < 0:
                    attributeLine[c][ind][1] = 0
                # print(attributeLine[c][ind])

        else:
            if typeP == 'normal' and c == 'verifyCode':
                continue
            attributeLine[c][0] = attributeLine[c][0] - wAxis * attributeLine[c][2]
            attributeLine[c][1] = attributeLine[c][1] - hAxis * attributeLine[c][3]
            attributeLine[c][2] = attributeLine[c][2] * (1 + 2 * wAxis)
            attributeLine[c][3] = attributeLine[c][3] * (1 + 2 * hAxis)
            if attributeLine[c][0] < 0:
                attributeLine[c][0] = 0
            if attributeLine[c][1] < 0:
                attributeLine[c][1] = 0

    # if typeP == 'elec' and pars == dict(textline_method='simple'):
    #     attributeLine['invoiceCode'] = decWidth(attributeLine['invoiceCode'], float(86.0 / 220.0))
    #     attributeLine['invoiceNo'] = decWidth(attributeLine['invoiceNo'], float(88.0 / 178.0))
    #     if 'invoiceDate' in attributeLine.keys():
    #         attributeLine['invoiceDate'] = decWidth(attributeLine['invoiceDate'], float(86.0 / 221.0))
    #     for ind, c in enumerate(attributeLine['verifyCode']):
    #         attributeLine['verifyCode'][ind] = decWidth(attributeLine['verifyCode'][ind], float(90.0 / 324.0))

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

    surfaceImagePath = jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp/" + \
                       jwkj_get_filePath_fileName_fileExt(filepath)[1] + "/origin.jpg"

    cv2.imwrite(surfaceImagePath, pipe.surface_image)
    filepathS = surfaceImagePath
    # img = Image.open(filepathS)  # 若为simple 方法 调用pipe后的图为初始图
    #
    # # 二值化
    # im = img.convert('L')
    # img = np.array(im)
    # h, w = img.shape
    #
    # # 是否采用自适应二值化方法
    # # isAdoptive = False
    # if type == 'elec':
    #     isAdoptive = False  # 测试中
    # else:
    #     isAdoptive = True  # 测试中
    #
    # thresholding = 160
    #
    # if isAdoptive:
    #     # 自适应二值化
    #     img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)
    # else:
    #     # 手动二值化
    #     for i in range(h):
    #         for j in range(w):
    #             if img[i, j] > thresholding:
    #                 img[i, j] = 255
    #             else:
    #                 img[i, j] = 0
    #
    # # 二值化图路径
    #
    # binaryzationSurfaceImagePath = jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp/" + \
    #                                jwkj_get_filePath_fileName_fileExt(filepath)[1] + "/binaryzationSurfaceImage.jpg"
    #
    # cv2.imwrite(binaryzationSurfaceImagePath, np.array(img))

    # 生成行提取的图片
    # print("4")
    plt_rects = []
    for x in attributeLine:
        if x == 'verifyCode' and len(attributeLine[x]) == 2:
            plt_rects.append(attributeLine[x][0])
            plt_rects.append(attributeLine[x][1])
        else:
            plt_rects.append(attributeLine[x])
    # 显示
    # vis_textline0 = fp.util.visualize.rects(cv2.imread(surfaceImagePath, 0), plt_rects)
    # pl.imshow(vis_textline0)

    # 保存到line目录
    pltpath = filepath.replace("upload", "line")
    try:
        for x, y, w, h in plt_rects:
            p0 = int(round(x)), int(round(y))
            p1 = int(round(x + w)), int(round(y + h))
            cv2.rectangle(pipe.surface_image, p0, p1, (255, 0, 0), 4)

        cv2.imwrite(pltpath, pipe.surface_image)
        # pl.savefig(pltpath)
    except Exception as e:
        print("绘制行提取图片不支持bmp格式：{}".format(e))

    timer.toc(content="行提取图绘制")

    # print('in')

    jsonResult = CropPic(filepathS, attributeLine, 11, filepath, pars, typeP, debug=False,
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

    dic = xmlToDict.XmlTodict('/home/huangzheng/ocr/VATInvoiceSimpleMuban.xml')

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
        try:
            pl.savefig(pltpath)
        except Exception as e:
            print("绘制行提取图片不支持bmp格式：{}".format(e))

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


# def init(filepath, type='special', pars=dict(textline_method='simple')):
def init(filepath, type='special', pars=dict(textline_method='textboxes')):
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
            try:
                pl.savefig(pltpath)
            except Exception as e:
                print("绘制行提取图片不支持bmp格式：{}".format(e))

            resArray = getArrayFromStr(res[0])
            # print(resArray)
            js = InterfaceType.JsonInterface.invoice()
            js.setVATInvoiceFromArray(resArray, type)

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
    # dset1 = '/home/huangzheng/ocr/testPic/3simple/'
    # jpgs = fp.util.path.files_in_dir(dset, '.jpg')
    # for c in jpgs:
    #    print(c)
    #    # dset = 'D:/Development/data/2/'
    #    # c = 'Image_00147.jpg'
    #    init(os.path.join(dset, c), type='special', pars=dict(textline_method='textboxes'))
    #    init(os.path.join(dset1, c), type='special', pars=dict(textline_method='simple'))
    #    print('__________________________  ' + c + '  _______________________')

    # init('/home/huangzheng/ocr/Image_00181.jpg', type='special', pars=dict(textline_method='textboxes'))
    # init('/home/huangzheng/ocr/testPic/3/Image_00003.jpg', type='special', pars=dict(textline_method='simple'))
    # init('Image_00131.jpg', type='elec', pars=dict(textline_method='simple'))
    init('/home/huangzheng/ocr/testPic/1/Image_00129.jpg', type='normal', pars=dict(textline_method='simple'))
