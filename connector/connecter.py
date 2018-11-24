from OCR import OCR, dianpiao
import keras.backend.tensorflow_backend as K

global_model = OCR.load_model()
dianpiao_global_model = dianpiao.load_model()

def OCR(image_path, typeP, thresholding = 160):
    """
        用来连接OCR调用，通过home/views.py来预加载全局模型
        imgae_path 输入图片路径，识别图片为行提取结果
    """
    global global_model
    global dianpiao_global_model

    with K.get_session().graph.as_default():
        if typeP == 'elec':
            out, _ = dianpiao.predict(image_path, dianpiao_global_model, thresholding=thresholding)
        else:
            out, _ = OCR.predict(image_path, global_model, thresholding=thresholding)

    return out

# caffe 模型
# import fp.TextBoxes.detect_textline as dt
# global_caffe_model = dt.load_caffe_model()