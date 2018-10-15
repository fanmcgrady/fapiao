import numpy as np
import cv2


def valid_image(im, colored=-1):
    '''
    colored : 1 must be color image
              0 must be gray image
             -1 both are ok
    '''
    if im is None:
        return False
    if not isinstance(im, np.ndarray):
        return False
    if colored >= 0:
        if not (len(im.shape) == 3 if colored == 1 else 2):
            return False
    return True
        
def valid_rect(rect, strict=False):
    if rect is None:
        return False
    if len(rect) != 4:
        return False
    if strict:
        if rect[2] < 0 or rect[3] < 0:
            return False
    return True
    
def valid_rects(rects, strict=False):
    if rects is None:
        return False
    if not isinstance(rects, np.ndarray):
        return False
    if len(rects.shape) != 2:
        return False
    if rects.shape[1] != 4:
        return False
    if strict:
        for rect in rects:
            if rect[2] < 0 or rect[3] < 0:
                return False
    return True


def valid_size(size):
    if size is None:
        return False
    if len(size) != 2:
        return False
    if size[0] < 0 or size[1] < 0:
        return False
    return True


def is_colored(image, pix_diff_max=10, color_ratio_min=0.001):
    assert isinstance(image, np.ndarray)
    if len(image.shape) == 2:
        return False
    assert len(image.shape) == 3
    img_b, img_g, img_r = cv2.split(image)
    d0 = cv2.absdiff(img_b, img_g) > pix_diff_max
    d1 = cv2.absdiff(img_b, img_r) > pix_diff_max
    d2 = cv2.absdiff(img_r, img_g) > pix_diff_max
    c0 = cv2.countNonZero(d0.astype(np.uint8))
    c1 = cv2.countNonZero(d1.astype(np.uint8))
    c2 = cv2.countNonZero(d2.astype(np.uint8))
    image_are = image.shape[0] * image.shape[1]
    cc = (c0 + c1 + c2) / image_are
    if cc < color_ratio_min:
        return False
    return True


def is_binarized(image, gray_ratio_min=0.05):
    assert isinstance(image, np.ndarray)
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    central_gray = ((image > 50) * (image < 200)).astype(np.uint8)
    central_gray_count = cv2.countNonZero(central_gray)
    image_are = image.shape[0] * image.shape[1]
    central_gray_ratio = central_gray_count / image_are
    # print('central_gray_ratio', central_gray_ratio)
    if central_gray_ratio > gray_ratio_min:
        return False
    return True
