# coding=gbk


import json
import os
import sys

import Detect

import aircv as ac
import cv2
import xmlToDict
from PIL import Image
from aip import AipOcr

import InterfaceType.JsonInterface
import SemanticCorrect.posteriorCrt
from connector import connecter


# import jsonpath

# ��ȡͼƬ
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def Started_Ocr(filePath):
    image = get_file_content(filePath)

    # ����ͨ������ʶ��, ͼƬ����Ϊ����ͼƬ
    # client.basicGeneral(image);
    '''
        APP_ID = '11428388'
        API_KEY = '11csXD7HzXNhtZxebtmaBGMY'
        SECRET_KEY = '2eITx621Gydci2YUfuOd43fesAYhyPul'
        APP_ID = '11412279'
        API_KEY = 'HlZHGoy57bGaVqFgIt8D0Onz'
        SECRET_KEY = 'BjDp89wMg2InQprvRr20SZWjrTGFET6R'
        '''

    APP_ID = '11757125'
    API_KEY = 'mnr4S1KAr8t0C3Zjoc4rTbuv'
    SECRET_KEY = 'GDFyYtVioPFmDCi2bcw2UklNmCjoi1nr'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    # ����п�ѡ����
    options = {}
    options["recognize_granularity"] = "big"
    options["probability"] = "true"
    options["accuracy"] = "normal"
    options["detect_direction"] = "true"

    # ����������ͨ��Ʊ��ʶ��
    result = client.receipt(image, options)

    data = json.loads(json.dumps(result).encode().decode("unicode-escape"))
    if 'words_result' in data.keys():
        if len(data['words_result']) > 0:
            ocrResult = ""
            for i in list(data['words_result']):
                ocrResult += str(i['words'])
            '''if len(sys.argv) > 3:
                if sys.argv[3] == '-D':  # show detail
                    print(data['words_result'][0]['words'])'''
        else:
            print("data out of range")
            print(data)
            return ""
    else:
        print("key 'words' doesn't exist!")
        return ""
    '''if len(sys.argv)>3:
        if sys.argv[3]=='-D': #show detail
            print(type(data))'''

    # print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')).encode().decode("unicode-escape"))

    return ocrResult


def FindSymbol(filePath):
    imsrc = ac.imread(filePath)
    # imsrcgray = cv2.cvtColor(imsrc, cv2.COLOR_BGR2GRAY)
    imobj = ac.imread('figure.jpg')

    # find the match position
    pos = ac.find_template(imsrc, imobj)
    print(type(pos))
    circle_center_pos = pos['result']
    circle_radius = 50
    color = (0, 255, 0)
    line_width = 10

    # draw circle

    #    print("imsrc:"+imsrc)
    print("circle_center_pos:" + str(circle_center_pos))

    return circle_center_pos


'''
def Detect(filePath):
    # convert the image to grayscale
    gray = cv2.cvtColor(filePath, cv2.COLOR_BGR2GRAY)

    # compute the Scharr gradient magnitude representation of the images
    # in both the x and y direction
    gradX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)

    # blur and threshold the image
    blurred = cv2.blur(gradient, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)

    # construct a closing kernel and apply it to the thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # perform a series of erosions and dilations
    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)

    # find the contours in the thresholded image
    image, cnts, hierarchy = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)

    # if no contours were found, return None
    if len(cnts) == 0:
        return None

    # otherwise, sort the contours by area and compute the rotated
    # bounding box of the largest contour
    c = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
    rect = cv2.minAreaRect(c)
    box = np.int0(cv2.boxPoints(rect))

    # return the bounding box of the barcode
    return box
'''


def MakeFile1(box, filePath):
    # ���
    # ��Ʊ1 ��ɫ  �����Ƭ��

    def jwkj_get_filePath_fileName_fileExt(filename):
        (filepath, tempfilename) = os.path.split(filename);
        (shotname, extension) = os.path.splitext(tempfilename);
        return filepath, shotname, extension

    h = box.tolist()[0][1] - box.tolist()[1][1]
    w = box.tolist()[2][0] - box.tolist()[1][0]

    # [[526, 379], [526, 272], [634, 272], [634, 379]]
    # ���[48,62][205,118]          �յ�[412,61][572,116]

    templet = [[526, 379], [526, 272], [634, 272], [634, 379]]
    templetSt = [[48, 62], [270, 118]]
    # ԭ��[634,379]     dh1=56    dw1=157

    # listStandard = self.Detect(filePath).tolist()

    try:
        SecLeftUp = [box[3][0] - (int)((templet[3][0] - templetSt[0][0]) / (templet[3][0] - templet[1][0]) * w),
                     box[3][1] - (int)((templet[3][1] - templetSt[0][1]) / (templet[3][1] - templet[2][1]) * h)]
        SecRightBottom = [box[3][0] - (int)((templet[3][0] - templetSt[1][0]) / (templet[3][0] - templet[1][0]) * w),
                          box[3][1] - (int)((templet[3][1] - templetSt[1][1]) / (templet[3][1] - templet[2][1]) * h)]

    except:
        print("SecFile build error!")

    img = Image.open(filePath)
    secFilePath = img.crop((SecLeftUp[0], SecLeftUp[1], SecRightBottom[0], SecRightBottom[1]))

    if os.path.exists(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
                1]) == False:
        os.mkdir(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[1])

    sFP1 = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
        1] + "/" + jwkj_get_filePath_fileName_fileExt(filePath)[
               1] + "_01.jpg"
    secFilePath.save(sFP1)

    return sFP1;


def MakeFile2(box, filePath):
    # �յ�
    # ��Ʊ1 ��ɫ  �����Ƭ��

    def jwkj_get_filePath_fileName_fileExt(filename):
        (filepath, tempfilename) = os.path.split(filename);
        (shotname, extension) = os.path.splitext(tempfilename);
        return filepath, shotname, extension

    h = box.tolist()[0][1] - box.tolist()[1][1]
    w = box.tolist()[2][0] - box.tolist()[1][0]

    # [[526, 379], [526, 272], [634, 272], [634, 379]]
    # ���[48,62][205,118]          �յ�[412,61][572,116]

    templet = [[526, 379], [526, 272], [634, 272], [634, 379]]
    templetSt = [[412, 61], [640, 116]]
    # ԭ��[634,379]     dh1=56    dw1=157

    # listStandard = self.Detect(filePath).tolist()

    try:
        SecLeftUp = [box[3][0] - (int)((templet[3][0] - templetSt[0][0]) / (templet[3][0] - templet[1][0]) * w),
                     box[3][1] - (int)((templet[3][1] - templetSt[0][1]) / (templet[3][1] - templet[2][1]) * h)]
        SecRightBottom = [box[3][0] - (int)((templet[3][0] - templetSt[1][0]) / (templet[3][0] - templet[1][0]) * w),
                          box[3][1] - (int)((templet[3][1] - templetSt[1][1]) / (templet[3][1] - templet[2][1]) * h)]
    except:
        print("SecFile build error!")

    '''if len(sys.argv)>3:
        if sys.argv[3]=='-D': #show detail
            print("SecLeftUp[0]:" + str(SecLeftUp[0]) + "   SecLeftUp[1]:" + str(SecLeftUp[1]))
            print("SecRightBottom[0]:" + str(SecRightBottom[0]) + "   SecRightBottom[1]:" + str(SecRightBottom[1]))'''

    img = Image.open(filePath)
    secFilePath = img.crop((SecLeftUp[0], SecLeftUp[1], SecRightBottom[0], SecRightBottom[1]))

    sFP2 = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
        1] + "/" + jwkj_get_filePath_fileName_fileExt(filePath)[
               1] + "_02.jpg"
    secFilePath.save(sFP2)

    return sFP2;


def jwkj_get_filePath_fileName_fileExt(filename):  # ��ȡ·��
    (filepath, tempfilename) = os.path.split(filename);
    (shotname, extension) = os.path.splitext(tempfilename);
    return filepath, shotname, extension


def MakeFileN(templetStOrig, box, filePath, extraName):
    # ͨ��
    # ��Ʊ1 ��ɫ  �����Ƭ��

    h = box.tolist()[0][1] - box.tolist()[1][1]
    w = box.tolist()[2][0] - box.tolist()[1][0]

    # [[526, 379], [526, 272], [634, 272], [634, 379]]
    # ���[48,62][205,118]          �յ�[412,61][572,116]
    # ͨ��templetSt

    templet = [[526, 379], [526, 272], [634, 272], [634, 379]]
    # templetStOrig = [[412, 61], [572, 116]]

    # ԭ��[634,379]     dh1=56    dw1=157

    # listStandard = self.Detect(filePath).tolist()
    img = Image.open(filePath)
    try:

        SecLeftUp_w = box[3][0] - (int)((templet[3][0] - templetStOrig[0][0]) / (templet[3][0] - templet[1][0]) * w)
        SecLeftUp_h = box[3][1] - (int)((templet[3][1] - templetStOrig[0][1]) / (templet[3][1] - templet[2][1]) * h)
        if SecLeftUp_w < 0:
            SecLeftUp_w = 0
        if SecLeftUp_h < 0:
            SecLeftUp_h = 0

        SecRightBottom_w = box[3][0] - (int)(
            (templet[3][0] - templetStOrig[1][0]) / (templet[3][0] - templet[1][0]) * w)
        SecRightBottom_h = box[3][1] - (int)(
            (templet[3][1] - templetStOrig[1][1]) / (templet[3][1] - templet[2][1]) * h)

        if SecRightBottom_w > img.size[0]:
            SecRightBottom_w = img.size[0]
        if SecRightBottom_h > img.size[1]:
            SecRightBottom_h = img.size[1]

        '''SecLeftUp = [box[3][0] - (int)((templet[3][0] - templetStOrig[0][0]) / (templet[3][0] - templet[1][0]) * w),
                     box[3][1] - (int)((templet[3][1] - templetStOrig[0][1]) / (templet[3][1] - templet[2][1]) * h)]
        SecRightBottom = [box[3][0] - (int)((templet[3][0] - templetStOrig[1][0]) / (templet[3][0] - templet[1][0]) * w),
                          box[3][1] - (int)((templet[3][1] - templetStOrig[1][1]) / (templet[3][1] - templet[2][1]) * h)]
                          '''
        SecLeftUp = [SecLeftUp_w, SecLeftUp_h]
        SecRightBottom = [SecRightBottom_w, SecRightBottom_h]
        '''
        SecLeftUp = [box[3][0] - (int)((templet[3][0] - templetStOrig[0][0]) / (templet[3][0] - templet[1][0]) * w),
                     box[3][1] - (int)((templet[3][1] - templetStOrig[0][1]) / (templet[3][1] - templet[2][1]) * h)]
        SecRightBottom = [box[3][0] - (int)((templet[3][0] - templetStOrig[1][0]) / (templet[3][0] - templet[1][0]) * w),
                          box[3][1] - (int)((templet[3][1] - templetStOrig[1][1]) / (templet[3][1] - templet[2][1]) * h)]
        '''

    except:
        print("SecFile build error!")

    '''if len(sys.argv)>3:
        if sys.argv[3]=='-D': #show detail
            print("SecLeftUp[0]:" + str(SecLeftUp[0]) + "   SecLeftUp[1]:" + str(SecLeftUp[1]))
            print("SecRightBottom[0]:" + str(SecRightBottom[0]) + "   SecRightBottom[1]:" + str(SecRightBottom[1]))'''

    secFilePath = img.crop((SecLeftUp[0], SecLeftUp[1], SecRightBottom[0], SecRightBottom[1]))

    sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
        1] + "/" + jwkj_get_filePath_fileName_fileExt(filePath)[
               1] + "_" + extraName + ".jpg"
    secFilePath.save(sFPN)

    return sFPN;


def MakeFileM(templetStOrig, box, filePath, extraName):
    # ��Ʊ2 ��ɫ  �����Ƭ��

    h = box.tolist()[0][1] - box.tolist()[1][1]
    w = box.tolist()[2][0] - box.tolist()[1][0]

    # [[483, 439], [483, 259], [632, 259], [632, 439]]

    templet = [[483, 439], [483, 259], [632, 259], [632, 439]]
    img = Image.open(filePath)

    try:
        SecLeftUp_w = box[3][0] - (int)((templet[3][0] - templetStOrig[0][0]) / (templet[3][0] - templet[1][0]) * w)
        SecLeftUp_h = box[3][1] - (int)((templet[3][1] - templetStOrig[0][1]) / (templet[3][1] - templet[2][1]) * h)
        if SecLeftUp_w < 0:
            SecLeftUp_w = 0
        if SecLeftUp_h < 0:
            SecLeftUp_h = 0

        SecRightBottom_w = box[3][0] - (int)(
            (templet[3][0] - templetStOrig[1][0]) / (templet[3][0] - templet[1][0]) * w)
        SecRightBottom_h = box[3][1] - (int)(
            (templet[3][1] - templetStOrig[1][1]) / (templet[3][1] - templet[2][1]) * h)

        if SecRightBottom_w > img.size[0]:
            SecRightBottom_w = img.size[0]
        if SecRightBottom_h > img.size[1]:
            SecRightBottom_h = img.size[1]

        '''SecLeftUp = [box[3][0] - (int)((templet[3][0] - templetStOrig[0][0]) / (templet[3][0] - templet[1][0]) * w),
                     box[3][1] - (int)((templet[3][1] - templetStOrig[0][1]) / (templet[3][1] - templet[2][1]) * h)]
        SecRightBottom = [box[3][0] - (int)((templet[3][0] - templetStOrig[1][0]) / (templet[3][0] - templet[1][0]) * w),
                          box[3][1] - (int)((templet[3][1] - templetStOrig[1][1]) / (templet[3][1] - templet[2][1]) * h)]
                          '''
        SecLeftUp = [SecLeftUp_w, SecLeftUp_h]
        SecRightBottom = [SecRightBottom_w, SecRightBottom_h]

    except:
        print("SecFile build error!")

    '''if len(sys.argv) > 3:
        if sys.argv[3] == '-D':  # show detail
            print("SecLeftUp[0]:" + str(SecLeftUp[0]) + "   SecLeftUp[1]:" + str(SecLeftUp[1]))
            print("SecRightBottom[0]:" + str(SecRightBottom[0]) + "   SecRightBottom[1]:" + str(SecRightBottom[1]))'''

    secFilePath = img.crop((SecLeftUp[0], SecLeftUp[1], SecRightBottom[0], SecRightBottom[1]))

    if os.path.exists(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
                1]) == False:
        os.mkdir(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[1])

    sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
        1] + "/" + jwkj_get_filePath_fileName_fileExt(filePath)[
               1] + "_" + extraName + ".jpg"
    secFilePath.save(sFPN)

    return sFPN;


def MakeFileInV(templetStOrig, box, symbol, filePath, extraName, templet):
    # circle_center_pos:(755.0, 2159.0)
    # [[132, 1197], [132, 1000], [325, 1000], [325, 1197]]
    h = symbol[1] - (box.tolist()[0][1] + box.tolist()[1][1]) / 2
    w = symbol[0] - (box.tolist()[2][0] + box.tolist()[1][0]) / 2

    # templet = [[228.5, 1098.5], [755, 2159]]
    img = Image.open(filePath)
    # print("h:" + str(h))
    # print("w:" + str(w))
    # print(symbol[0]+"-("+templet[1][0]+"-"+templetStOrig[0][0]+"/"+templet[1][0]+"-"+templet[0][0] +"*"+str(h))

    try:
        SecLeftUp_w = symbol[0] - (int)((templet[1][0] - templetStOrig[0][0]) / (templet[1][0] - templet[0][0]) * w)
        SecLeftUp_h = symbol[1] - (int)((templet[1][1] - templetStOrig[0][1]) / (templet[1][1] - templet[0][1]) * h)
        if SecLeftUp_w < 0:
            SecLeftUp_w = 0
        if SecLeftUp_h < 0:
            SecLeftUp_h = 0

        # print("SecLeftUp[0]:" + str(SecLeftUp_w) + "   SecLeftUp[1]:" + str(SecLeftUp_h))

        SecRightBottom_w = symbol[0] - (int)(
            (templet[1][0] - templetStOrig[1][0]) / (templet[1][0] - templet[0][0]) * w)
        SecRightBottom_h = symbol[1] - (int)(
            (templet[1][1] - templetStOrig[1][1]) / (templet[1][1] - templet[0][1]) * h)

        if SecRightBottom_w > img.size[0]:
            SecRightBottom_w = img.size[0]
        if SecRightBottom_h > img.size[1]:
            SecRightBottom_h = img.size[1]

        '''SecLeftUp = [box[3][0] - (int)((templet[3][0] - templetStOrig[0][0]) / (templet[3][0] - templet[1][0]) * w),
                     box[3][1] - (int)((templet[3][1] - templetStOrig[0][1]) / (templet[3][1] - templet[2][1]) * h)]
        SecRightBottom = [box[3][0] - (int)((templet[3][0] - templetStOrig[1][0]) / (templet[3][0] - templet[1][0]) * w),
                          box[3][1] - (int)((templet[3][1] - templetStOrig[1][1]) / (templet[3][1] - templet[2][1]) * h)]
                          '''
        SecLeftUp = [SecLeftUp_w, SecLeftUp_h]
        SecRightBottom = [SecRightBottom_w, SecRightBottom_h]

    except:
        print("SecFile build error!")

    '''if len(sys.argv) > 3:
        if sys.argv[3] == '-D':  # show detail
            print("SecLeftUp[0]:" + str(SecLeftUp[0]) + "   SecLeftUp[1]:" + str(SecLeftUp[1]))
            print("SecRightBottom[0]:" + str(SecRightBottom[0]) + "   SecRightBottom[1]:" + str(SecRightBottom[1]))'''

    secFilePath = img.crop((SecLeftUp[0], SecLeftUp[1], SecRightBottom[0], SecRightBottom[1]))

    if os.path.exists(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
                1]) == False:
        os.mkdir(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[1])

    sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
        1] + "/" + jwkj_get_filePath_fileName_fileExt(filePath)[
               1] + "_" + extraName + ".jpg"
    secFilePath.save(sFPN)

    return sFPN;


def OcrPic(secFilePath):
    '''
    data = json.loads(json.dumps(Started_Ocr(secFilePath)).encode().decode("unicode-escape"))
    print(type(data))
    print(type(data['words_result'][0]['words']))
    '''
    return Started_Ocr(secFilePath)

    # return data['words_result'][0]['words']  # .encode().decode("unicode-escape"))
    '''
        except:
            print("Print error")
        else:
            #self.label_2.setText(json.dumps(OcrT.result).encode().decode("unicode-escape"))
            print("run succeed!")
            '''


def OcrNoPic(filePath):
    image = get_file_content(filePath)

    # ����ͨ������ʶ��, ͼƬ����Ϊ����ͼƬ
    # client.basicGeneral(image);
    '''
        APP_ID = '11428388'
        API_KEY = '11csXD7HzXNhtZxebtmaBGMY'
        SECRET_KEY = '2eITx621Gydci2YUfuOd43fesAYhyPul'
        APP_ID = '11412279'
        API_KEY = 'HlZHGoy57bGaVqFgIt8D0Onz'
        SECRET_KEY = 'BjDp89wMg2InQprvRr20SZWjrTGFET6R'
        '''

    APP_ID = '11757125'
    API_KEY = 'mnr4S1KAr8t0C3Zjoc4rTbuv'
    SECRET_KEY = 'GDFyYtVioPFmDCi2bcw2UklNmCjoi1nr'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    # ����п�ѡ����
    options = {}
    options["language_type"] = "CHN_ENG"
    options["detect_direction"] = "true"
    options["detect_language"] = "true"
    options["probability"] = "true"

    # ����������ͨ��Ʊ��ʶ��
    result = client.basicGeneral(image, options)

    data = json.loads(json.dumps(result).encode().decode("unicode-escape"))
    if 'words_result' in data.keys():
        if len(data['words_result']) > 0:
            ocrResult = ""
            for i in list(data['words_result']):
                ocrResult += str(i['words'])
            '''if len(sys.argv) > 3:
                if sys.argv[3] == '-D':  # show detail
                    print(data['words_result'][0]['words'])'''
        else:
            print("data out of range")
            print(data)
            return ""
    else:
        print("key 'words' doesn't exist!")
        return ""
    '''if len(sys.argv)>3:
        if sys.argv[3]=='-D': #show detail
            print(type(data))'''

    # print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')).encode().decode("unicode-escape"))

    return ocrResult


def DetectBlueTrainTicket(box, filePath):
    secP1 = MakeFile1(box, filePath)
    # print(type(secP1))
    # print(secP1)

    secP2 = MakeFile2(box, filePath)
    # print(type(secP2))
    # print(secP2)

    result1 = OcrPic(secP1)
    # print(type(result1))
    # print(result1)

    result2 = OcrPic(secP2)
    # print(type(result2))
    # print(result2)

    # �˿���Ϣ
    templetStPassagerInfo = [[22, 276], [328, 314]]
    secP4 = MakeFileN(templetStPassagerInfo, box, filePath, 'PassagerInfo')
    result4 = OcrPic(secP4)
    # �˿���Ϣ
    templetStPassagerInfoName = [[328, 276], [478, 314]]
    secP4_1 = MakeFileN(templetStPassagerInfoName, box, filePath, 'PassagerInfoName')
    result4_1 = OcrPic(secP4_1)

    # ����
    templetStTrainNum = [[264, 62], [434, 119]]
    secP3 = MakeFileN(templetStTrainNum, box, filePath, 'trainNum')
    result3 = OcrPic(secP3)

    # ����ʱ��
    templetStTrainTime = [[24, 139], [393, 181]]
    secP5 = MakeFileN(templetStTrainTime, box, filePath, 'trainTime')
    result5 = OcrPic(secP5)

    # ��λ
    templetStSeatNum = [[408, 138], [568, 178]]
    secP6 = MakeFileN(templetStSeatNum, box, filePath, "seatNum")
    result6 = OcrPic(secP6)

    # ��������
    templetStSeatType = [[407, 175], [597, 214]]
    secP7 = MakeFileN(templetStSeatType, box, filePath, "seatType")
    result7 = OcrPic(secP7)

    # ��Ʊ��
    templetStCheckNum = [[507, 24], [631, 66]]
    secP8 = MakeFileN(templetStCheckNum, box, filePath, "checkNum")
    result8 = OcrPic(secP8)

    # Ʊ��
    templetStPrice = [[33, 177], [184, 216]]
    secP9 = MakeFileN(templetStPrice, box, filePath, "price")
    result9 = OcrPic(secP9)

    # ��Ʊ��
    templetStTicketsNum = [[21, 10], [216, 76]]
    secP10 = MakeFileN(templetStTicketsNum, box, filePath, "ticketsNum")
    result10 = OcrPic(secP10)

    '''
    line1 = "���վ:   " + result1 + "\t    �յ�վ: " + result2
    line2 = "���Σ�    " + result3 + "\t    ����ʱ��:" + result5
    line3 = "�˿���Ϣ�� " + result4 + "\t    ��λ:" + result6 + "\t    ��������:" + result7
    line4 = "��Ʊ�ڣ�    " + result8 + "\t    Ʊ��:" + result9

    {
        'departCity':[48, 62,270-48, 118-62],
        'arriveCity':[412, 61,640-412, 116-61],
        'trainNumber':[264, 62, 434-264, 119-62],
        'invoiceDate':[24, 139, 393-24, 181-139],
        'seatNum':[408, 138, 568-408, 178-138],
        'idNum':[22, 276, 328-22, 314-276],
        'passenger':[328, 276, 478-328,314-276],
        'price':[33, 177, 184-33, 216-177],
        'ticketsNum':[21, 10, 216-21, 76-10]

        }

    print(line1)
    print(line2)
    print(line3)
    print(line4)
    '''
    # �����
    pC = SemanticCorrect.posteriorCrt.posteriorCrt()
    pC.setTrainTicketPara(result1, result2, result3, result5, result6, result4, result4_1,
                          result9)  # (self, departCity, arriveCity, trainNumber, invoiceDate, seatNum, idNum, passenger)
    pC.startTrainTicketCrt()

    # �������
    js = InterfaceType.JsonInterface.invoice()
    js.addTrainCardInfo(pC.dic['departCity'], pC.dic['arriveCity'], pC.dic['trainNumber'], pC.dic['invoiceDate'],
                        pC.dic['price'], pC.dic['seatNum'], pC.dic['passenger'], pC.dic['idNum'], result10, '0000',
                        '0000')
    # ʼ��վ���յ�վ�����Σ����ڣ�����λ�ţ����������֤�ţ���Ʊ���
    jsoni = js.dic
    print(jsoni)

    # return json.dumps(jsoni).encode().decode("unicode-escape")
    return json.dumps(jsoni).encode().decode("unicode-escape")


def DetectVATInvoice(box, symbol, filePath):  # ʶ����ֵ˰��Ʊ����1

    # ��λ��ά��

    # ��λ��

    dic = xmlToDict.XmlTodict('ModeLabel_00001.xml')

    tplt = [dic['QRCode'][0], dic['QRCode'][1], dic['figureX'][2], dic['figureX'][3]]
    for c in tplt:
        if c == None:
            print('Templet VATInvoice error')

    for item in dic:
        if item != 'QRCode' and item != 'figureX':
            # print(item)
            tmp = MakeFileInV(
                [[int(dic.get(item)[0]), int(dic.get(item)[1])], [int(dic.get(item)[2]), int(dic.get(item)[3])]], box,
                symbol, filePath, item, tplt)

            print(item + ":   " + OcrPic(tmp))

    js = InterfaceType.JsonInterface.invoice()
    js.addVATInvoiceInfo


def DetectRedTrainTicket(box, filePath):
    # ��ɫ��Ʊʶ��

    # ���
    templetStStartPlace = [[29, 74], [247, 128]]
    secP1 = MakeFileM(templetStStartPlace, box, filePath, 'StartPlace')
    result1 = OcrPic(secP1)

    templetStEndPlace = [[425, 68], [649, 132]]
    secP2 = MakeFileM(templetStEndPlace, box, filePath, 'EndPlace')
    result2 = OcrPic(secP2)

    # ����
    templetStTrainNum = [[230, 65], [433, 127]]
    secP3 = MakeFileM(templetStTrainNum, box, filePath, 'trainNum')
    result3 = OcrPic(secP3)

    # �˿���Ϣ
    templetStPassagerInfo = [[0, 343], [350, 388]]
    secP4 = MakeFileM(templetStPassagerInfo, box, filePath, 'PassagerInfo')
    result4 = OcrPic(secP4)

    # �˿���Ϣname
    '''templetStPassagerInfoName = [[0, 343], [350, 388]]
    secP4_1 = MakeFileM(templetStPassagerInfoName, box, filePath, 'PassagerInfo')
    result4_1 = OcrPic(secP4_1)
    '''

    # ����ʱ��
    templetStTrainTime = [[0, 163], [357, 204]]
    secP5 = MakeFileM(templetStTrainTime, box, filePath, 'trainTime')
    result5 = OcrPic(secP5)

    # ��λ
    templetStSeatNum = [[392, 164], [595, 210]]
    secP6 = MakeFileM(templetStSeatNum, box, filePath, "seatNum")
    result6 = OcrPic(secP6)

    # ��������
    templetStSeatType = [[425, 211], [552, 254]]
    secP7 = MakeFileM(templetStSeatType, box, filePath, "seatType")
    result7 = OcrPic(secP7)

    # ����
    templetStCheckNum = [[34, 40], [236, 87]]
    secP8 = MakeFileM(templetStCheckNum, box, filePath, "trainNo")
    result8 = OcrPic(secP8)

    # Ʊ��
    templetStPrice = [[3, 206], [215, 258]]
    secP9 = MakeFileM(templetStPrice, box, filePath, "price")
    result9 = OcrPic(secP9)

    # ������
    templetStPrice = [[0, 388], [319, 428]]
    secP10 = MakeFileM(templetStPrice, box, filePath, "TraintNoNum")
    result10 = OcrPic(secP10)

    '''
    line1 = "���վ:   " + result1 + "\t    �յ�վ: " + result2
    line2 = "���Σ�    " + result3 + "\t    ����ʱ��:" + result5
    line3 = "�˿���Ϣ�� " + result4 + "\t    ��λ:" + result6 + "\t    ��������:" + result7
    line4 = "���ţ�    " + result8 + "\t    Ʊ��:" + result9
    line5 = "������:   " + result10

    {
        'departCity':[29,74,247-29,128-74],
        'arriveCity':[425,68,649-425,132-68],
        'trainNumber':[230, 65, 433-230, 127-65],
        'invoiceDate':[0,163, 357,204-163],
        'seatNum':[392,164, 595-392, 210-164],
        'idNum':[0,343, 350,388-343],
        'passenger':[-1,-1,0,0],
        'price':[3,206, 215-3, 258-206],
        'ticketsNum':[34,40, 236-34,87-40]

        }




    print(line1)
    print(line2)
    print(line3)
    print(line4)
    print(line5)
    '''
    # �����
    pC = SemanticCorrect.posteriorCrt.posteriorCrt()
    pC.setTrainTicketPara(result1, result2, result3, result5, result6, result4,
                          '',
                          result9)  # (self, departCity, arriveCity, trainNumber, invoiceDate, seatNum, idNum, passenger)
    pC.startTrainTicketCrt()

    js = InterfaceType.JsonInterface.invoice()

    js.addTrainCardInfo(pC.dic['departCity'], pC.dic['arriveCity'], pC.dic['trainNumber'], pC.dic['invoiceDate'],
                        pC.dic['price'], pC.dic[
                            'seatNum'], '', pC.dic['idNum'], result10, '0000',
                        '0000')  # ʼ��վ���յ�վ�����Σ����ڣ�����λ�ţ����������֤�ţ���Ʊ���

    jsoni = js.dic

    # print(jsoni)
    # return json.dumps(jsoni).encode().decode("unicode-escape")
    return json.dumps(jsoni).encode().decode("unicode-escape")


def cropToOcr(filePath, recT, typeT, debug=False, isusebaidu=True):
    ocrResult = {}
    img = Image.open(filePath)

    if os.path.exists(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
                1]) == False:
        os.mkdir(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
                1])

    # ������ʶ��ocrģ�ͣ���ֵ˰רƱģ�ͣ�������typeTΪ11����
    for x in recT:
        sp = img.crop((recT[x][0], recT[x][1], recT[x][0] + recT[x][2], recT[x][1] + recT[x][3]))

        sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
            1] + "/" + jwkj_get_filePath_fileName_fileExt(filePath)[
                   1] + "_" + x + ".jpg"
        sp.save(sFPN)

        if debug == False:
            # if (x != 'invoiceNo'):
            # # �������ʶ�𲢲����������岻��ʶ�������
            isusebaidu = False
            if isusebaidu:
                midResult = OcrPic(sFPN)
            else:
                print("==============================Using OCR3=========================")
                midResult = connecter.OCR(sFPN, 'normal', 'verifyCode')
            # else:
            #     midResult = OcrNoPic(sFPN)

            print(midResult + '   isUseBaidu: ' + str(isusebaidu))
            ocrResult[x] = midResult

    print(ocrResult)
    pC = SemanticCorrect.posteriorCrt.posteriorCrt()

    if typeT == 11 and debug == False:
        import OcrForVat
        if ocrResult['invoiceDate'][:4] == '��Ʊ����' or len(ocrResult['invoiceDate']) < 4:
            recT['invoiceDate'] = OcrForVat.mubanDetectInvoiceDate(filePath)['invoiceDate']
            sp = img.crop((recT['invoiceDate'][0], recT['invoiceDate'][1],
                           recT['invoiceDate'][0] + recT['invoiceDate'][2],
                           recT['invoiceDate'][1] + recT['invoiceDate'][3]))

            sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + \
                   jwkj_get_filePath_fileName_fileExt(filePath)[
                       1] + "/" + jwkj_get_filePath_fileName_fileExt(filePath)[
                       1] + "_" + 'invoiceDateFix' + ".jpg"
            sp.save(sFPN)

            midResult = OcrPic(sFPN)

            print('invoiceDateFix: ' + midResult)
            ocrResult['invoiceDate'] = midResult

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

    return json.dumps(jsoni).encode().decode("unicode-escape"), json.dumps(ocrResult).encode().decode("unicode-escape")


def detect(filePath, recT, type):
    # ���ýӿ�
    # type:1 ����Ʊ
    # type:2 ���Ʊ
    # type:3 ��Ʊ
    if os.access(filePath, os.F_OK):
        if type == 1:
            box = Detect.detect(cv2.imread(filePath), 1)
            jsR = DetectBlueTrainTicket(box, filePath)
            # print(jsR)
            return jsR

        if type == 2:
            box = Detect.detect(cv2.imread(filePath), 1)
            jsR = DetectRedTrainTicket(box, filePath)
            # print(jsR)
            return jsR

        if type == 3:
            box = Detect.detect(cv2.imread(filePath), 0.3)
            symbol = FindSymbol(filePath)
            jsR = DetectVATInvoice(box, symbol, filePath)
            # print(jsR)
            return jsR

    else:
        print("Can't open file " + filePath)


def __init__():
    chooseMod = 1
    if len(sys.argv) > 1:
        filePath = sys.argv[1]
        print("ʶ���ļ�filePath:" + filePath)

        if len(sys.argv) > 2:
            if sys.argv[2] == '1':
                chooseMod = 1
            # Ĭ����ɫ��Ʊ
            if sys.argv[2] == '2':
                chooseMod = 2
                print("mod:" + str(chooseMod))
                # ��ɫ��Ʊ
            if sys.argv[2] == '11':
                chooseMod = 3
                # ר����ֵ˰��Ʊ1

    else:
        filePath = 'Image_00066.jpg'
        print("ʶ���ļ�filePath:")
        print("Ĭ���ļ���Image_00068.jpg")

    if os.access(filePath, os.F_OK):
        if chooseMod == 1:
            box = Detect.detect(cv2.imread(filePath), 1)
            print(DetectBlueTrainTicket(box, filePath))

        if chooseMod == 2:
            box = Detect.detect(cv2.imread(filePath), 1)
            print(DetectRedTrainTicket(box, filePath))
        if chooseMod == 3:
            box = Detect.detect(cv2.imread(filePath), 0.3)
            symbol = FindSymbol(filePath)
            print(DetectVATInvoice(box, symbol, filePath))
    else:
        print("Can't open file " + filePath)

# __init__()

# print(OcrNoPic('./tmp/Image_00008/Image_00008_invoiceNo.jpeg'))
