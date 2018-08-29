from PIL import Image
import numpy as np
from glob import glob
import heapq
import json
import time

# 计算汉字间的距离，最后保存为json数据

# 定义领域大小
near = 0.90 # cos


"""
返回格式
{
    参考字：{领域字： 相似度}
}

举例
{
    "A": { "A":"0" , "B":"1" },
    "B": { "A":"0" , "B":"1" }
}
"""


# 1. 从磁盘中取出所有的图片
# 2. 计算当前

# 获取文件夹下的所有.png文件名, 返回文件名list
# dir举例 ./Unicode/
def getImgFromDir(dir):
    file_list = glob(dir+"/*.png")
    return file_list

# 获取Unicode路径图片的路径中的汉字字符
def getUnicode(address):
    return address[8:-4]

# 获取Common路径图片的路径中的汉字字符
def getCommon(address):
    return address[7:-4]

# 获取文件
def readImg(img_address):
    return Image.open(img_address)

# 保存数据
def save_to_file(file_name, contents):
    fh = open(file_name, 'w')
    fh.write(contents)
    fh.close()


# 计算两个图片之间的距离
def computeDistance(img1, img2):
    gray_img1 = img1.convert('L')
    gray_img2 = img2.convert('L')
    # 计算过程中发现有的图片不一样的，resize一下
    gray_img1 = gray_img1.resize((128, 145))
    gray_img2 = gray_img2.resize((128, 145))

    # 归一化
    np_gray_img1 = np.array(gray_img1) / 255 
    np_gray_img2 = np.array(gray_img2) / 255

    # img1 * img2 / |img1| |img2|
    img1_mul_img2 = np.sum(np_gray_img1 * np_gray_img2)
    img1_module = np.sqrt(np.sum(np_gray_img1 * np_gray_img1))
    img2_module = np.sqrt(np.sum(np_gray_img2 * np_gray_img2))
    distance = img1_mul_img2 / (img1_module * img2_module)
    return distance

# 获取最接近的Top个向量
def getTop(dict, unicode, top_num):
    nlargestList = heapq.nlargest(top_num, dict[unicode].values())
   
    for value in nlargestList:                                #输出结果
        for key in dict[unicode]:
            if dict[unicode][key] == value:
                print(key, dict[unicode][key])
    return nlargestList

# 传入数据和需要过滤的距离，生成新的数据
def fliterDistance(dic, distance):
    for uni_key in dic.keys():
        uni_dic = dic[uni_key]
        # 删除时用list包裹迭代器
        for com_key in list(uni_dic.keys()):
            val = uni_dic[com_key]
            if val < distance:
                del uni_dic[com_key]
    return dic

# 一键删除
def delete_all(dic):
    f = open("dele.txt", 'r', encoding='utf-8')
    Chinese = f.readline()
    dic = delete_words(dic, Chinese)
    dic = delete_self(dic)
    return dic

# 载入字典
def load_dict(dict_file):
    f = open(dict_file, "r")
    json_data = f.readline()
    dic =  json.loads(json_data)
    return dic 

# 删除不常用汉字
def delete_words(dic, string):
    for key in dic:
        for com_key in list(dic[key].keys()):
            for word in string:
                if com_key == word:
                    del dic[key][com_key]
    return dic

# 删除和查询字相同的字
def delete_self(dic):
    for key in dic:
        for com_key in list(dic[key].keys()):
            if com_key == key:
                del dic[key][com_key]
    return dic


# 字典切片
dict_slice = lambda adict, start, end: { k:adict[k] for k in list(adict.keys())[start:end] }

# 找到最大的前*个相同字
def find_nearest_words(dic, top):
    for key in dic:
        dic[key] = dict_slice(dic[key], 0, top)
    return dic

# 保存字典
def storeDict(dic, file_name):
    dict_json = json.dumps(dic)
    save_to_file(file_name, dict_json)

# 对字典进行排序
def sortedDict(dic):
    for key in dic:
        dic[key] = dict(sorted(dic[key].items(), key=lambda item:item[1], reverse=True))
    return dic


# 生成完整的Data样本
def __init__():
    # 获取 Unicode 的所有汉字
    unicode_list = getImgFromDir("UnicodeSong")
    count_of_unicode = len(unicode_list)
    # print(len(unicode_list))
    # print(unicode_list[0][8:-4])
    # 获取 Common 的所有汉字
    common_list = getImgFromDir("CommonSong")
    count_of_common = len(common_list)
    # 测试一下相关文件是否按照顺序排列好，如果不是还应该对所有文件进行排序
    # 是否真的需要排序，对应的查询是以汉字作为key的


    # 构造List，遍历循环所有unicode_list中包含的字
    # 构造字典每个unicode汉字对应一个字典，字典中key为common汉字，value为对应相似度
    dict_all_words = {}
    percent = 0
    time0 = time.time()
    for i in range(count_of_unicode):
    #for i in range(count_of_unicode):
        s = getUnicode(unicode_list[i])
        # print(s)
        imgU = readImg(unicode_list[i])
        dict = {}
        for j in range(count_of_common):
            imgC = readImg(common_list[j])
            sC = getCommon(common_list[j])
            c = computeDistance(imgU, imgC)
            dict[sC] = c
        if i % 21 == 0:
            percent = percent + 0.1
            print(str(percent) + "% " + "epend time: " + str(time.time() - time0))
            time0 = time.time()
        dict_all_words[s] = dict
        

    print(len(dict_all_words))
    words_json = json.dumps(dict_all_words)
    # 测试
    # getTop(dict_all_words, '嘴', 20)
    # 保存数据
    save_to_file("song_distance.json", words_json)
    

#__init__()


#img = readImg('./Unicode/一.png')
#img1 = readImg('./Unicode/天.png')
#print(computeDistance(img, img))