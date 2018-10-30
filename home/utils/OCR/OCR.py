import time

import cv2
import keras.backend.tensorflow_backend as K
import numpy as np
from PIL import Image

from home import views

char = ''
with open(r'home/utils/OCR/rcnn_dic.txt', encoding='utf-8') as f:
    for ch in f.readlines():
        ch = ch.strip('\r\n')
        char = char + ch
char = char + '卍'
print('nclass:', len(char))
n_classes = len(char)

char_to_id = {j: i for i, j in enumerate(char)}
id_to_char = {i: j for i, j in enumerate(char)}


class Timer(object):
    def __init__(self):
        self.total_time = 0.
        self.calls = 0
        self.start_time = 0.
        self.diff = 0.
        self.average_time = 0.

    def tic(self):
        self.start_time = time.time()

    def toc(self, average=True):
        self.diff = time.time() - self.start_time
        self.total_time += self.diff
        self.calls += 1
        self.average_time = self.total_time / self.calls
        if average:
            return self.average_time
        else:
            return self.diff


def predict(img_path, base_model, thresholding=160):
    """
        thresholding 输入范围 0 - 255
        默认为160
        0 : 采用自动阈值
        > 0 : 采用人工设置的阈值
    """
    if thresholding > 255:
        thresholding = 255
    if thresholding < 0:
        thresholding = 0

    t = Timer()
    img = Image.open(img_path)
    im = img.convert('L')
    scale = im.size[1] * 1.0 / 64
    w = im.size[0] / scale
    w = int(w)
    # print('w:',w)

    im = im.resize((160, 32), Image.ANTIALIAS)
    img = np.array(im)
    h, w = img.shape

    if thresholding == 0:
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)
    else:
        for i in range(h):
            for j in range(w):
                if img[i, j] > thresholding:
                    img[i, j] = 255
                else:
                    img[i, j] = 0

    img = np.array(img)

    img = img.astype(np.float32) / 255.0 - 0.5
    X = img.reshape((32, 160, 1))
    X = np.array([X])

    t.tic()
    y_pred = base_model.predict(X)
    t.toc()
    # print("times,",t.diff)
    argmax = np.argmax(y_pred, axis=2)[0]
    y_pred = y_pred[:, :, :]
    out = K.get_value(K.ctc_decode(y_pred, input_length=np.ones(y_pred.shape[0]) * y_pred.shape[1], )[0][0])[:, :]
    out = u''.join([id_to_char[x] for x in out[0]])

    return out, im


def OCR(image_path):
    """
        imgae_path 输入图片路径，识别图片为行提取结果
        color: 0 二值， 1 灰度， 2 彩色
        base_model 为加载模型，这个模型最好在服务器启动时加载，计算时作为参数输入即可，减少加载模型所需要的时间
    """
    base_model = views.global_model
    out, _ = predict(image_path, base_model)

    return out

    # if  __name__ == "__main__":
    #     files = os.listdir("/home/huangzheng/ocr/tmp/Image_00002")
    i = np.random.randint(0, len(files))
    # for i in range(len(files)):
    #     test_image = r'/home/huangzheng/ocr/tmp/Image_00002/' + files[i]
    #     out = OCR(test_image)
    #     print('预测图片为: /home/huangzheng/ocr/tmp/Image_00002/' + files[i] + ' ， 预测结果为：', out)
