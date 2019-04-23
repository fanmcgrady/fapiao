import copy
import glob
import cv2
import matplotlib.pyplot as pl
from PIL import Image
# 加载黄政的代码
import sys
sys.path.append("/home/huangzheng/ocr")
from Get_Chinese_Info import Get_Chinese_Info
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,2,3"
import OCR

from connector import FindCircle, flow, connecter

import json

import numpy as np
import SemanticCorrect.posteriorCrt
import fp
import fp.TextBoxes.recog_invoice_type
import caffe
import InterfaceType
import lineToAttribute.getAtbt
import xmlToDict
import muban

from connector.TicToc import Timer
import time
from connector import PipelineInit
global_pipeline = PipelineInit.PipelineInit()

def jwkj_get_filePath_fileName_fileExt(filename):  # 提取路径
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def newOcr(filepath, typeP, x):
    return connecter.OCR(filepath, typeP, x)


def CropPic(filePath, recT, origin_filePath, pars, typeP, debug=False, isusebaidu=False):
    ocrResult = {}

    time1 = time.time()
    # -----------------------------------------------------------二值化---------------------
    img = Image.open(filePath)
    imgL = Image.open(filePath)  # 若为simple 方法 调用pipe后的图为初始图

    imL = imgL.convert('L')
    imgL = np.array(imL)

    # 是否采用自适应二值化方法
    isAdoptive = False
    if typeP != 'elec':  # 测试中
        hist, _ = np.histogram(imgL, bins=[0, 50, 100, 150, 200, 255])
        all = imgL.shape[0] * imgL.shape[1]
        t = hist[0] + hist[-1]
        if t / all < 0.95:
            isAdoptive = True  # 测试中

    timex = time.time()
    # print("判断   " + str(timex - time1))

    # print("isAdoptive:  " + str(isAdoptive))
    if isAdoptive:
        # 自适应二值化
        imgL = cv2.adaptiveThreshold(imgL, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)

    # 二值化图路径
    binaryzationSurfaceImagePath = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/binaryzationSurfaceImage.jpg"
    cv2.imwrite(binaryzationSurfaceImagePath, np.array(imgL))
    imgL = Image.open(binaryzationSurfaceImagePath)
    # ----------------------------------------------------二值化 ---------------------------------

    # 裁剪（校验码处理）
    time2 = time.time()

    # print('二值化过程:   ' + str(time2 - time1))

    # 校验码处理
    threshold = fp.core.thresh.HybridThreshold(rows=1, cols=4, local='gauss')

    for x in recT:
        if x == 'verifyCode' and len(recT[x]) == 2:
                sp1 = imgL.crop(
                    (
                        recT[x][0][0], recT[x][0][1], recT[x][0][0] + recT[x][0][2],
                        recT[x][0][1] + recT[x][0][3]))
                sp2 = imgL.crop(
                    (
                        recT[x][1][0], recT[x][1][1], recT[x][1][0] + recT[x][1][2],
                        recT[x][1][1] + recT[x][1][3]))
        elif x == 'invoiceNo':
            sp = img.crop((recT[x][0], recT[x][1], recT[x][0] + recT[x][2], recT[x][1] + recT[x][3]))
        else:
            sp = imgL.crop((recT[x][0], recT[x][1], recT[x][0] + recT[x][2], recT[x][1] + recT[x][3]))

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

            # print('--------------  ---------------' + sFPN1)
            # print('--------------  ---------------' + sFPN2)
        else:
            sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + '/' + jwkj_get_filePath_fileName_fileExt(filePath)[
                1] + "_" + x + ".jpg"
            # print('--------------  ---------------' + sFPN)
            sp.save(sFPN)
            if typeP == 'normal' and x == 'verifyCode':
                imcv = cv2.imread(sFPN, 1)[:, :, 2]
                bi_im = threshold(imcv)
                cv2.imwrite(sFPN, bi_im)

        if debug == False:
            if isusebaidu:
                midResult = flow.OcrPic(sFPN)
            else:
                midResult = ''
                if x == 'verifyCode':  # 是校验码时需要判断大于19位
                    if len(recT[x]) == 2:  # 两个框的情况
                        midResult1 = newOcr(sFPN1, typeP, x)
                        midResult2 = newOcr(sFPN2, typeP, x)
                        midResult += midResult1 if len(midResult1) > 19 else ''
                        midResult += midResult2 if len(midResult2) > 19 else ''
                    else:
                        mdrs = newOcr(sFPN, typeP, x)
                        midResult = mdrs if len(mdrs) > 19 else ''  # 超过20位为疑似校验码
                elif x == 'invoiceCode':
                    # 发票代码目前只有10位和12位两种，当预测结果为11位时只取后10位
                    # 摘自税务局官网： http://www.chinatax.gov.cn/n810341/n810765/n812193/n813008/c1203713/content.html
                    # 对于12位的普通发票 第1位为国家税务局、地方税务局代码，1为国家税务局、2为地方税务局，0为总局
                    # 因此对于普通发票预测结果为12位的代码，如果是第一位不是0、1、2则认为误判，只取后十位
                    midResult = newOcr(sFPN, typeP, x)
                    if len(midResult) > 12:  # 超过12位的直接取后12位
                        midResult = midResult[-12:]

                    if len(midResult) == 11:
                        midResult = midResult[-10:]
                    elif len(midResult) == 12 and typeP == "normal":
                        if midResult[0] not in ['0', '1', '2']:
                            midResult = midResult[-10:]
                else:
                    midResult = newOcr(sFPN, typeP, x)

            # print(midResult + '   isUseBaidu: ' + str(isusebaidu))
            ocrResult[x] = midResult

    # 后矫正
    time6 = time.time()
    # print('切图识别：    ' + str(time6 - time2))

    # print(ocrResult)
    pC = SemanticCorrect.posteriorCrt.posteriorCrt()

    # print("origin_filePath " + origin_filePath)

    js = InterfaceType.JsonInterface.invoice()
    pC.setVATParaFromVATDict(ocrResult)
    if (typeP == 'normal' or typeP == 'special') and ('invoiceNoS' in pC.VATdic.keys()):
        tms = pC.VATdic['invoiceNoS']
        pC.VATdic['invoiceNoS'] = pC.VATdic['invoiceNo']
        pC.VATdic['invoiceNo'] = tms
        # print('Use  invoiceNoS ---------------------------------')
    pC.startVATCrt()
    js.setValueWithDict(pC.VATdic)
    jsoni = js.dic

    time7 = time.time()
    # print('后矫正： ' + str(time7 - time6))

    return json.dumps(jsoni).encode().decode("unicode-escape")


def newMubanDetect(filepath, typeP='special', pars=dict(textline_method='textboxes'), timer=None):
    # print(typeP)
    # print(pars)

    # pipe = fp.vat_invoice.pipeline.VatInvoicePipeline(typeP, pars=pars, debug=False)  # 请用debug=False
    pipe = global_pipeline.get_pipe(typeP)
    im = cv2.imread(filepath, 1)

    pipe(im)
    timer.toc(content="行提取")

    attributeLine = {}

    atbDic = {
        'type': 'invoiceCode',
        'serial': 'invoiceNo',
        'time': 'invoiceDate',
        'tax_free_money': 'invoiceAmount',
        'serial_tiny': 'invoiceNoS'}

    if pipe.predict('verify') is not None:
        # 由于目前不论普票专票的分类结果都是spec_and_normal_bw，因此337行的处理结果都是Normal
        # 在此通过行提取是否有校验码一项来判别普票和专票，普票则加入校验码项，专票则更改类型
        atbDic['verify'] = 'verifyCode'
    else:
        typeP = 'special'

    for atb in atbDic.keys():
        if not pipe.predict(atb) is None:
            attributeLine[atbDic[atb]] = list(pipe.predict(atb))

    wAxis = 0.02
    hAxis = 0.1

    for c in attributeLine:
        # print(attributeLine[c])
        if c in ['invoiceNo', 'invoiceAmount']:
            continue

        if c == 'verifyCode' and len(attributeLine[c]) == 2:
            # 校验码提取到两个框
            for i in range(len(attributeLine[c])):
                attributeLine[c][i][0] = attributeLine[c][i][0] - wAxis * attributeLine[c][i][2]
                attributeLine[c][i][1] = attributeLine[c][i][1] - hAxis * attributeLine[c][i][3]
                attributeLine[c][i][2] = attributeLine[c][i][2] * (1 + 2 * wAxis)
                attributeLine[c][i][3] = attributeLine[c][i][3] * (1 + 2 * hAxis)
                if attributeLine[c][i][0] < 0:
                    attributeLine[c][i][0] = 0
                if attributeLine[c][i][1] < 0:
                    attributeLine[c][i][1] = 0
        else:
            # 非校验码的情况
            attributeLine[c][0] = attributeLine[c][0] - wAxis * attributeLine[c][2]
            attributeLine[c][1] = attributeLine[c][1] - hAxis * attributeLine[c][3]
            attributeLine[c][2] = attributeLine[c][2] * (1 + 2 * wAxis)
            attributeLine[c][3] = attributeLine[c][3] * (1 + 2 * hAxis)
            if attributeLine[c][0] < 0:
                attributeLine[c][0] = 0
            if attributeLine[c][1] < 0:
                attributeLine[c][1] = 0

    # print(attributeLine)
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

    # 如为simple方法 先存储pipe。surface_image为初始图（后续识别定位基于该图）

    surfaceImagePath = jwkj_get_filePath_fileName_fileExt(filepath)[0] + "/tmp/" + \
                       jwkj_get_filePath_fileName_fileExt(filepath)[1] + "/origin.jpg"

    cv2.imwrite(surfaceImagePath, pipe.surface_image)
    filepathS = surfaceImagePath

    plt_rects = []
    for x in attributeLine:
        if x == 'verifyCode' and len(attributeLine[x]) == 2:
            plt_rects.append(attributeLine[x][0])
            plt_rects.append(attributeLine[x][1])
        else:
            plt_rects.append(attributeLine[x])

    # 保存到line目录
    pltpath = filepath.replace("upload", "line")
    try:
        for x, y, w, h in plt_rects:
            p0 = int(round(x)), int(round(y))
            p1 = int(round(x + w)), int(round(y + h))
            cv2.rectangle(pipe.surface_image, p0, p1, (255, 0, 0), 4)

        cv2.imwrite(pltpath, pipe.surface_image)
    except Exception as e:
        pass
        # print("绘制行提取图片不支持bmp格式：{}".format(e))

    timer.toc(content="行提取图绘制")

    jsonResult = CropPic(filepathS, attributeLine, filepath, pars, typeP, debug=False,
                         isusebaidu=False)  # ocr和分词
    timer.toc(content="切图ocr识别")
    # print(jsonResult)

    return jsonResult


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
def init(filepath, pars=dict(textline_method='textboxes')):  # type='special',
    '''
    mage = cv2.imread(filepath,0)
    str_info, position = recog_qrcode(image, roi=None)

    #二维码无法识别
    if str_info == None:
    '''
    timer = Timer()
    timer.tic()

    recog = fp.TextBoxes.recog_invoice_type.InvoiTypeRecog()
    im = caffe.io.load_image(filepath)

    invoice_type = ['spec_and_normal', 'spec_and_normal']
    typeP = invoice_type[recog(im)]

    if typeP == 'spec_and_normal':
        # typeP = 'special'
        typeP = 'normal'
    elif typeP == 'spec_and_normal_bw':
        typeP = 'normal'
    else:
        return "", timer, typeP

    return newMubanDetect(filepath, typeP, pars, timer)


def batch_test():
    # 参数表： 测试图片集路径，结果存储路径，发票类型
    curr = time.strftime('%Y.%m.%d', time.localtime(time.time()))

    do_ocr = "y"
    if len(sys.argv) == 1:
        images_dir = input("Please enter pictures dir:")
        result_save_path = input("Please enter result save path:")
        invoicetype = input("Please enter the invoice type(special=01, normal=04):")
    elif len(sys.argv) == 4:
        images_dir = sys.argv[1]
        result_save_path = sys.argv[2]
        invoicetype = sys.argv[3]
    elif len(sys.argv) == 5:
        images_dir = sys.argv[1]
        result_save_path = sys.argv[2]
        invoicetype = sys.argv[3]
        do_ocr = sys.argv[4]
    else:
        print("Wrong input args.\n")
        return

    root_path = result_save_path
    result_save_path = os.path.join(result_save_path, curr)
    if not os.path.exists(result_save_path):
        os.makedirs(result_save_path)

    image_list = glob.glob(os.path.join(images_dir, "*.jpg"))
    if len(image_list) == 0:
        image_list = glob.glob(os.path.join(images_dir, "*.bmp"))
        if len(image_list) == 0:
            print("No pics in "+images_dir+" !\n")
            return
    num_of_imges = len(image_list)

    if do_ocr == "y" or do_ocr == "Y":
        # 是否执行ocr操作
        print("Now begin to ocr...")
        ocr_result = []
        ocr_erorr_list = []
        for img in image_list:
            try:
                tuple_info = json.loads(init(img))
                tuple_info['filename'] = img
                ocr_result.append(tuple_info)
            except Exception as _:
                ocr_erorr_list.append(img)
        print("ocr is complete, get %d / %d pics info." % (len(ocr_result), num_of_imges))

        file_ocr_result = os.path.join(result_save_path, "ocr_result.json")
        file_ocr_error_list = os.path.join(result_save_path, "ocr_error_files.txt")

        print("Now saving the result...")
        with open(file_ocr_result, 'w') as re, open(file_ocr_error_list, 'w') as er:
            re.write(json.dumps(ocr_result, indent=4, ensure_ascii=False))
            for i in ocr_erorr_list:
                er.writelines(i+'\n')
    else:
        # 不执行ocr直接用已有结果对比chinese_info.json
        file_ocr_result = os.path.join(result_save_path, "ocr_result.json")
        with open(file_ocr_result, "r", encoding="utf-8") as fp:
            content = fp.read()
            content = content.replace('¥', '￥')
            if content.startswith(u'\ufeff'):
                content = content.encode('utf8')[3:].decode('utf8')
            ocr_result = json.loads(content)

    print("Chinese infor query begin...")
    succeed, query_error = Get_Chinese_Info(ocr_result, result_save_path, invoicetype, root_path)

    file_result = str(succeed) + "(%d)_ocr_correct.txt" % num_of_imges
    file_result = os.path.join(result_save_path, file_result)

    try:
        with open(file_result, "w") as wp:
            wp.writelines(file_result + " %.2f " % (succeed/num_of_imges)+'\n')
            wp.writelines("%d not find in web：没有查询到中文数据（不一定ocr错误）"%(num_of_imges-succeed)+'\n')
            wp.writelines("%d query_error_pics：本地有中文数据，但五元组错误"%(query_error)+'\n')
            # wp.writelines("%d ocr_error_files：ocr没有正确生成五元组"%(len(ocr_erorr_list))+'\n')
    except Exception as e:
        print(e)
    finally:
        print("Test end.")


def train_ticket_batch_test(tickets_path, Type):
    # 火车票批测试，返回ocr结果json
    import Ocr
    tickets_ocr_rsult = []

    tickets_list = glob.glob(tickets_path+"/*.jpg")
    print(tickets_list)
    for tk_path in tickets_list:
        print("******************"+tk_path+"**********************")
        try:
            tk_result, _ = Ocr.init(tk_path, Type)
            tickets_ocr_rsult.append(tk_result)
        except Exception as e:
            print(e)

    return tickets_ocr_rsult


if __name__ == '__main__':
    # batch_test()
    save_path = "/home/huangzheng/wangtao/20190423.20.BlueTrainTicket/result.json"
    js = train_ticket_batch_test("/home/huangzheng/wangtao/20190423.20.BlueTrainTicket", "blue")
    with open(save_path, 'w') as wp:
        wp.write(js)
    print("end")