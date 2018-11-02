import os
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


class DataPathText(object):
    def __init__(self, dset_root, txt_file):
        if not os.path.isfile(txt_file):
            print('File {} do not exist!'.format(txt_file))
            return
        self.content = None
        self.dset_root = dset_root
        self.idx = 0
        with open(txt_file, 'r') as fp:
            content = fp.read()
            content = content.split('\n')
            content = [line.strip() for line in content]
            content = [line for line in content if len(line) > 0]
            content = [line for line in content if line[0] != '#']
            content = sorted(content)
            content = [os.path.join(self.dset_root, line) for line in content]
            self.content = content

    def next_path(self):
        if self.idx < len(self.content):
            data_path = self.content[self.idx]
        else:
            data_path = None
        self.idx += 1
        return data_path

    def reset(self):
        self.idx = 0
