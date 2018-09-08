import numpy as np
import cv2

def is_blue(image, noise=5):
    '''Return True if it is a blue ticket, otherwise red ticket'''
    b, g, r = cv2.split(image)
    #cv2.calcHist(images, channels, mask, histSize, ranges)
    blue_count = np.count_nonzero(b > r + noise) # sure blue
    red_count = np.count_nonzero(r > b + noise)
    return blue_count > red_count

class UpsideDownCheck_BlueTTK(object):
    def __init__(self, pix_remove_ratio=0.1):
        self.pix_remove_ratio = pix_remove_ratio
        self.check_height_ratio = 0.125
        
    def __region_check(self, roi):
        r, s = self.pix_remove_ratio, 1. - self.pix_remove_ratio
        v0, v1 = np.min(roi), np.max(roi)
        vv0 = r * v1 + s * v0
        vv1 = s * v1 + r * v0
        return np.mean(roi[np.logical_and(roi > vv0, roi < vv1)])

    def __call__(self, image,):
        '''Check if the ticket is upside down,
        as the ticket may be misplaced during scanning'''
        im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h_check = int(image.shape[0] * self.check_height_ratio)
        top_mean = self.__region_check(im[:h_check, :])
        bot_mean = self.__region_check(im[-h_check:, :])
        print('mean: top {}, bot {}'.format(top_mean, bot_mean))
        return top_mean < bot_mean

class UpsideDownCheck_v2(object):
    def __init__(self, debug=False):
        self.check_height_ratio = 0.135
        self.check_width_ratio = 0.265
        self.debug = dict() if debug else None
    
    def __call__(self, image):
        h, w = image.shape[:2]
        hc = int(h * self.check_height_ratio)
        wc = int(w * self.check_width_ratio)
        roi0 = image[:hc,  :wc ]
        roi1 = image[-hc:, -wc:]
        if self.debug is not None:
            self.debug['roi0'] = roi0
            self.debug['roi1'] = roi1
        mean0 = self._check_roi(roi0)
        mean1 = self._check_roi(roi1)
        #print(mean0, mean1)
        return self._redness(mean0) < self._redness(mean1)
    
    def _check_roi(self, roi):
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray_roi = cv2.GaussianBlur(gray_roi, (3, 3), 1.4)
        bin_roi = cv2.adaptiveThreshold(gray_roi, 255, cv2.ADAPTIVE_THRESH_MEAN_C,\
                                      cv2.THRESH_BINARY, 11, 15)
        mean_pix = np.mean(roi[np.where(bin_roi == 0)], axis=0)
        return mean_pix
    
    def _redness(self, color):
        b, g, r = color
        return max(r - 0.5 * (b + g), 0)