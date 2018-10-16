import numpy as np
import cv2

def make_caffe_data(image):
    '''image is from cv2.imread()'''
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.astype(np.float32)
    image_max = np.max(image)
    image_min = np.min(image)
    image = (image - image_min) / (image_max - image_min)
    return image