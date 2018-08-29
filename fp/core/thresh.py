import numpy as np
import cv2

debug = True
if debug:
    import matplotlib.pyplot as pl

def adaptive_otsu_surface(image, rows, cols):
    '''Adapitve Otsu threshold method'''
    assert len(image.shape) == 2
    h, w = image.shape
    
    y_step = int(np.ceil(h / rows))
    x_step = int(np.ceil(w / cols))
    thmap = np.zeros((rows, cols), np.uint8)
    for j, y0 in enumerate(range(0, h, y_step)):
        y1 = min(y0 + y_step, h)
        for i, x0 in enumerate(range(0, w, x_step)):
            x1 = min(x0 + x_step, w)
            sub_im = image[y0 : y1, x0 : x1]
            th, _ = cv2.threshold(sub_im, 120, 255, cv2.THRESH_OTSU)
            thmap[j, i] = th
    thmap = cv2.GaussianBlur(thmap, (3,3), 1.2)
    thmap = cv2.resize(thmap, (w, h), interpolation=cv2.INTER_LINEAR)
    return thmap
    
def adaptive_otsu(image, rows, cols):
    thmap = adaptive_otsu_surface(image, rows, cols)
    imblur = cv2.GaussianBlur(image, (3,3), 1.2)
    result = cv2.compare(imblur, thmap, cv2.CMP_GT)
    return result

def local_mean_surface(image, ksize, c):
    surf = cv2.boxFilter(image, ddepth=-1, ksize=ksize)
    surf[surf <= c] = 0
    surf[surf > c] -= c
    return surf


class _Threshold(object):
    def __init__(self):
        pass
    
    def __call__(self, image):
        raise NotImplemented
        
class AdaptiveOtsuThreshold(_Threshold):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
    
    def __call__(self, image):
        thmap = adaptive_otsu_surface(image, self.rows, self.cols)
        imblur = cv2.GaussianBlur(image, (3,3), 1.2)
        result = cv2.compare(imblur, thmap, cv2.CMP_GT)
        return result
    
class LocalMeanThreshold(_Threshold):
    def __init__(self, ksize=11, c=3):
        self.size = ksize
        self.c = c
    
    def __call__(self, image):
        imblur = cv2.GaussianBlur(image, (3,3), 1.2)
        thr = cv2.adaptiveThreshold(imblur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
                                    cv2.THRESH_BINARY, self.size, self.c)
        return thr
    
class LocalGaussianThreshold(_Threshold):
    def __init__(self, ksize=11, c=3):
        self.size = ksize
        self.c = c
    
    def __call__(self, image):
        imblur = cv2.GaussianBlur(image, (3,3), 1.2)
        thr = cv2.adaptiveThreshold(imblur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                    cv2.THRESH_BINARY, self.size, self.c)
        return thr
        
class HybridThreshold(_Threshold):
    def __init__(self, rows, cols, ksize=11, c=3):
        self.rows = rows
        self.cols = cols
        self.ksize = (ksize, ksize)
        self.c = c
    
    def __call__(self, image, mixr):
        otsu_surf = adaptive_otsu_surface(image, self.rows, self.cols)
        mean_surf = local_mean_surface(image, self.ksize, self.c)
        surf = cv2.addWeighted(otsu_surf, mixr, mean_surf, 1.-mixr, 0)

        imblur = cv2.GaussianBlur(image, (3,3), 1.2)
        #sobelx = cv2.Sobel(imblur, cv2.CV_32F, 1, 0, ksize=5)  # x
        #sobely = cv2.Sobel(imblur, cv2.CV_32F, 0, 1, ksize=5)  # y
        #ratio = np.sqrt(sobelx**2 + sobely**2)
        #ratio = (ratio * 255.0 / np.max(ratio)).astype(np.uint8)
        #_, ratiox = cv2.threshold(ratio, 1, 255, cv2.THRESH_OTSU)  
        #h_size = ratiox.shape[1], ratiox.shape[0]
        #l_size = tuple([int(0.2 * i) for i in h_size])
        #ratiox = cv2.resize(ratiox, l_size)
        #ratiox = cv2.GaussianBlur(ratiox, (3,3), 1.2)
        #ratiox = cv2.resize(ratiox, h_size)
        #ratiox = ratiox.astype(np.float32) / 255.
        #iratio = 1.0 - ratiox
        #surf = mean_surf.astype(np.float32) * ratiox + otsu_surf.astype(np.float32) * iratio
        #surf = surf.astype(np.uint8)
        surf = cv2.addWeighted(mean_surf, 0.8, otsu_surf, 0.2, 0.0)
        result = cv2.compare(imblur, surf, cv2.CMP_GT)
        
        #if debug:
        #    pl.figure(figsize=(15,18))
        #    pl.subplot(4,2,1)
        #    pl.imshow(otsu_surf, 'gray')
        #    pl.subplot(4,2,2)
        #    pl.imshow(cv2.compare(imblur, otsu_surf, cv2.CMP_GT), 'gray')
        #    pl.subplot(4,2,3)
        #    pl.imshow(mean_surf, 'gray')
        #    pl.subplot(4,2,4)
        #    pl.imshow(cv2.compare(imblur, mean_surf, cv2.CMP_GT), 'gray')
        #    pl.subplot(4,2,5)
        #    pl.imshow(ratio, 'gray')
        #    pl.subplot(4,2,6)
        #    pl.imshow(ratiox, 'gray')
        #    pl.subplot(4,2,7)
        #    pl.imshow(surf, 'gray')
        #    pl.subplot(4,2,8)
        #    pl.imshow(result, 'gray')
        #    
            
        return result