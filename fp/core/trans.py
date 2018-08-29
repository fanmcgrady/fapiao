import numpy as np
import cv2


def rotate_crop(src_image, center, angle, dsize, border_color=(255,255,255)):
    trans_mat = cv2.getRotationMatrix2D(center, angle, scale=1.0)
    trans_mat[0, 2] -= (center[0] - 0.5 * dsize[0])
    trans_mat[1, 2] -= (center[1] - 0.5 * dsize[1])
    img = cv2.warpAffine(src_image, trans_mat, dsize, borderValue=border_color)
    return img

def warp(src_image, src_points, dsize, border_color=(255,255,255)):
    w, h = 1. * dsize
    src_points = np.array(src_points).astype(np.float32)
    dst_points = np.array([[0,0], [0,h], [w,h], [w,0]]).astype(np.float32)
    cv2.getPerspectiveTransform(src_points, dst_points)
    img = cv2.warpPerspective(src_image, trans_mat, dsize, borderValue=border_color)
    return img

class Trans(object):
    def __init__(self):
        pass
    
    def __call__(self, image):
        pass
        
        
def rotate180(image):
    '''rotate the image in 180 degrees, used when the image is upside down'''
    return np.fliplr(np.flipud(image))