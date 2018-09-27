import numpy as np
import cv2
import os
from PIL import Image
from matplotlib import pyplot as plt

def detect(image, rate):
    # convert the image to grayscale
    gray_ = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    h, w = gray_.shape
    #print(h, w)
    gray = cv2.resize(gray_, (int(w * rate), int(h * rate)))

    # compute the Scharr gradient magnitude representation of the images
    # in both the x and y direction
    gradX = cv2.Sobel(gray, ddepth = cv2.CV_32F, dx = 1, dy = 0, ksize = -1)
    gradY = cv2.Sobel(gray, ddepth = cv2.CV_32F, dx = 0, dy = 1, ksize = -1)
 
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
    closed = cv2.erode(closed, None, iterations = 4)
    closed = cv2.dilate(closed, None, iterations = 4)
 
    # find the contours in the thresholded image
    image,cnts,hierarchy = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
 
    # if no contours were found, return None
    if len(cnts) == 0:
        return None
 
    # otherwise, sort the contours by area and compute the rotated
    # bounding box of the largest contour
    c = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
    rect = cv2.minAreaRect(c)
    box = np.int0(cv2.boxPoints(rect))
    box = np.int0(box / rate)
    # return the bounding box of the barcode
    '''
    print(type(box))

    gray_ = cv2.line(gray_, (box[0][0], box[0][1]), (box[1][0], box[1][1]), 0, 5)
    gray_ = cv2.line(gray_, (box[1][0], box[1][1]), (box[2][0], box[2][1]), 0, 5)
    gray_ = cv2.line(gray_, (box[2][0], box[2][1]), (box[3][0], box[3][1]), 0, 5)
    gray_ = cv2.line(gray_, (box[3][0], box[3][1]), (box[0][0], box[0][1]), 0, 5)
    print(box)
    plt.imshow(gray_, 'gray')
    plt.show()
    '''
    return box


def jwkj_get_filePath_fileName_fileExt(filename):
    (filepath, tempfilename) = os.path.split(filename);
    (shotname, extension) = os.path.splitext(tempfilename);
    return filepath, shotname, extension

'''
img = Image.open("E:/DevelopT/pycharm_workspace/Ocr/Image_00001.jpg")
print(type(img))


print(type(jwkj_get_filePath_fileName_fileExt('Image_00001.jpg')))
print(jwkj_get_filePath_fileName_fileExt('Image_00001.jpg')[1])
'''

# print(detect(cv2.imread('TR003.jpg'),2.0  ).tolist())
