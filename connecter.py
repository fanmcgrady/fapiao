from OCR.OCR import *

def OCR(image_path):
    """
        用来连接OCR调用，通过home/views.py来预加载全局模型
        imgae_path 输入图片路径，识别图片为行提取结果
    """
    from home import views
    global_model = views.global_model

    with K.get_session().graph.as_default():
        out, _ = predict(image_path, global_model)

    return out