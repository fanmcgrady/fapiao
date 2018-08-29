import numpy as np
import cv2

def find_quads(binary_image, approx_ratio=0.02, min_area=50):
    _, contours, _ = cv2.findContours(binary_image.copy(), mode=cv2.RETR_EXTERNAL, 
                                      method=cv2.CHAIN_APPROX_SIMPLE)
    quads = []
    conts = []
    for cont in contours:
        # approximate the contour
        peri = cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, approx_ratio * peri, True)

        # if the approximated contour has four points, then assume that the
        # contour is a book -- a book is a rectangle and thus has four vertices
        if len(approx) == 4 and cv2.isContourConvex(approx) \
            and cv2.contourArea(approx) > min_area:
            # approx.shape is (4,1,2), so, use squeeze
            quads.append(np.squeeze(approx))
            conts.append(cont)
            
    return np.array(quads), conts

def draw_quad(image, quad):
    cv2.line(image, tuple(quad[0]), tuple(quad[1]), color=(255,0,0))
    cv2.line(image, tuple(quad[1]), tuple(quad[2]), color=(0,255,0))
    cv2.line(image, tuple(quad[2]), tuple(quad[3]), color=(0,0,255))
    cv2.line(image, tuple(quad[3]), tuple(quad[0]), color=(255,0,255))
    return image