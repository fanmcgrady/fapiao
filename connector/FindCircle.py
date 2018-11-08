# coding=utf-8


import os

import aircv as ac
import cv2

# image = cv2.imread('')

# 转灰度
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# print circle_center_pos
'''def draw_circle(img, pos, circle_radius, color, line_width):
    cv2.circle(img, pos, circle_radius, color, line_width)
    cv2.imshow('objDetect', imsrc)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
'''


def jwkj_get_filePath_fileName_fileExt(filename):  # 提取路径
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def findSymbol(filePath):
    # define an area [600-1000, 950-1450]

    if os.path.exists(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
                1]) == False:
        os.makedirs(
            jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[1])

    sFPN = jwkj_get_filePath_fileName_fileExt(filePath)[0] + "/tmp/" + jwkj_get_filePath_fileName_fileExt(filePath)[
        1] + "/" + jwkj_get_filePath_fileName_fileExt(filePath)[
               1] + "_GRAY.jpg"
    im = cv2.imread(filePath)  # 读取图片
    GrayImage = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    ret, im_gray = cv2.threshold(GrayImage, 190, 255, cv2.THRESH_BINARY)  # 转换二值化
    cv2.imwrite(sFPN, im_gray)

    '''
    plt.imshow(im_gray, 'gray')
    plt.title('1')
    plt.xticks([]), plt.yticks([])


    plt.show()
    '''

    imsrc = ac.imread(sFPN)
    # imsrcgray = ac.cvtColor(imsrc, cv2.COLOR_BGR2GRAY)
    imobj = ac.imread('/home/huangzheng/ocr/figureX.jpg')
    # imobjgray = ac.cvtColor(imobj, cv2.COLOR_BGR2GRAY)

    # find the match position
    pos = ac.find_template(imsrc, imobj, 0.3)
    if pos['result'] == None:
        imobj = ac.imread('/home/huangzheng/ocr/figure.jpg')
        pos = ac.find_template(imsrc, imobj, 0.5)
    # print(type(pos))

    # define an area [600-1000, 950-1450]添加定位符区域确认
    if not (pos['result'][0] > 600 and pos['result'][0] < 1000 and pos['result'][1] > 950 and pos['result'][1] < 1450):
        imobj = ac.imread('/home/huangzheng/ocr/figureX1.jpg')
        pos = ac.find_template(imsrc, imobj, 0.5)

    circle_center_pos = pos['result']
    circle_radius = 50
    color = (0, 255, 0)
    line_width = 10

    # draw circle

    #    print("imsrc:"+imsrc)
    print("circle_center_pos:" + str(circle_center_pos))
    return circle_center_pos[0], circle_center_pos[1]
    # draw_circle(imsrc, circle_center_pos, circle_radius, color, line_width)

# print(findSymbol('Image_00188.jpg'))
