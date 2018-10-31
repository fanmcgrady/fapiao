import os
from OCR import OCR

if __name__ == "__main__":
    files = os.listdir("/home/huangzheng/ocr/tmp/Image_00002")
    for i in range(len(files)):
        test_image = r'/home/huangzheng/ocr/tmp/Image_00002/' + files[i]
        out = OCR(test_image)
        print('预测图片为: ' + test_image + '， 预测结果为：', out)
