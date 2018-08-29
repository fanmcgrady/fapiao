# -*- coding: utf-8 -*-
#为了方便，字典原始文件与本文件应位于同一目录下
#删除其他保留汉字re.sub("[A-Za-z0-9\!\%\[\]\#\+\&\*\-\+\—\.\,\。\·\'\"\{\}\:]",'',str)
#删除其他保留ascii('[^\x00-\x7f]')，其中^表示取反
#删除其他保留汉字(r'[^\u4e00-\u9fa5]')，其中r表示raw string无视转义符反斜杠，str=repr(str)同理

'''
使用示例：
global_dict = readTXTintoPydictwithFreq("动物.txt")
print("这里打印结果：大黄蜂！！！！！！")
print(selectFromPydict("大黄蜂"))

接口规范：
函数readTXTintoPydictwithFreq(txtName):读原始字典，返回一个python字典结构
入口参数为“火车站.txt”。示例：readTXTintoPydict("火车站.txt")

函数selectFromPydict(str):查询接口，返回值为int
>0 #查询完成，所查词在字典中,并返回词频
-1 #错误代码，初始值，程序未正常运行
-2 #错误代码，词典数据有误
-3 #错误代码，词典中没有这个词
'''



import re

#以下函数提供查询方
#需要先给全局变量赋值，示例：global_list = readTXTintoPydictwithFreq("火车站.txt")
global_dict = {}
def selectFromPydict(str):
    flag = -1 #错误代码，初始值，程序未正常运行
    if str in global_dict.keys():
        flag = global_dict[str] #查询完成，所查词在字典中,并返回词频
        if flag <= 0:
            flag = -2 #错误代码，词典数据有误
    else:
        flag = -3 #错误代码，词典中没有这个词
    return flag

#以下函数读原始字典，并重组为python字典结构
#入口参数为“火车站.txt”。示例：readTXTintoPydict("火车站.txt")
def readTXTintoPydictwithFreq(txtName):
    pydict = {}
    p = ''
    with open(txtName, encoding="gbk") as txt:
        for line in txt:
            temp1 = re.sub("[A-Za-z0-9\!\%\[\]\#\+\&\*\-\+\—\.\,\。\·\'\"\{\}\:]", "", line)
            temp1 = temp1.replace(" ", "").strip()
            #hashcode = obtainUTFHashCode(temp1)
            freq = re.sub('[^0-9]', "", line) #只取数字
            freq = freq.replace(" ","").strip()
            if freq == '' :
                freq = 1
            freq = int(freq)
            pydict[temp1] = freq
    #print(pydict)
    return pydict


#以下码段用于读写原始字典，并重组为json
#源字典txt文件都采用gbk编码，新生成json文件采用utf-8编码
#入口参数为“原始字典名.txt，生成文件名.json”。示例：readTXTintoJSON("火车站.txt","StationDict.json")
def readTXTintoJSON(txtName,jsonName):
    dict_list = []
    with open(txtName,"r", encoding="gbk") as txt:
        #print(txt.read()) #只要在这里先打印了txt的内容，下面的for就不再执行？
        for line in txt:
            temp1 = re.sub("[A-Za-z0-9\!\%\[\]\#\+\&\*\-\+\—\.\,\。\·\'\"\{\}\:]", "", line)
            temp1 = temp1.replace(" ", "").strip()
            hashcode = obtainUTFHashCode(temp1)
            dict_list.append("\""+temp1+"\""+":"+"["+str(hashcode)+"]")#hashcode放到[]里方便扩展
        #print("写入信息打印：\n")
        #print(dict_list)

    with open(jsonName, "a+", encoding="utf-8") as json:
        json.write("{")
        for element in dict_list:
            if dict_list.index(element) < len(dict_list)-1:
                json.write(element+","+"\n")
            elif dict_list.index(element) == len(dict_list)-1:
                json.write(element + "\n")
            else:
                json.write("下标为："+str(dict_list.index(element))+"的数据出错"+ "\n")
        json.write("}")
        json.close()

#读带有单词频数的字典，并输出json
def readTXTintoJSONwithFreq(txtName,jsonName):
    dict_list = []
    with open(txtName,"r", encoding="gbk") as txt:
        #print(txt.read()) #只要在这里先打印了txt的内容，下面的for就不再执行？
        for line in txt:
            temp1 = re.sub("[A-Za-z0-9\!\%\[\]\#\+\&\*\-\+\—\.\,\。\·\'\"\{\}\:]", "", line)
            temp1 = temp1.replace(" ", "").strip()
            hashcode = obtainUTFHashCode(temp1)
            dict_list.append("\""+temp1+"\""+":"+"["+str(hashcode)+","+"freq"+"]")
        #print("写入信息打印：\n")
        #print(dict_list)

    with open(jsonName, "a+", encoding="utf-8") as json:
        json.write("{")
        for element in dict_list:
            if dict_list.index(element) < len(dict_list)-1:
                json.write(element+","+"\n")
            elif dict_list.index(element) == len(dict_list)-1:
                json.write(element + "\n")
            else:
                json.write("下标为："+str(dict_list.index(element))+"的数据出错"+ "\n")
        json.write("}")
        json.close()

#以下代码段用于构造hashcode
def obtainUTFCode(string):
    result = '查UTF的函数未正确执行'
    result_list = []
    result = string
    char_list = re.findall(r'.{1}', result)
    #print("打印单字切分列表：" + str(len(char_list)))
    #print(char_list)
    for char in char_list:
        #print(char)
        result = ord(char)
        result_list.append(result)
        #print("打印结果：" + str(result))

    #print(result_list)
    return result_list

# 16个汉字字长作为单词最长标准，对应32bit的二进制存储，十进制即：2147483648~4294967296
# "这里是个一点都不萌萌哒的单词示例"
def obtainUTFHashCode(string):
    hashCode = -1  # 错误代码，初始值，程序未正常运行
    utf_list = obtainUTFCode(string)
    for utf in utf_list:
        #print(utf)
        hashCode += utf * (2 ** utf_list.index(utf))
        #print(hashCode)
    #print(bin(hashCode))

    if hashCode < 2147483648 and hashCode > 0:
        hashCode += 2147483648
    elif hashCode > 4294967296:
        hashCode = -2  # 错误代码，输入单词过长，需要重新分词
    else:
        hashCode = -3  # 错误代码，程序已经运行

    if hashCode > 4294967296 or hashCode < 2147483648:
        hashCode = -4  # 错误代码，超出计算范围或者输入不是汉字

    #print('定长到32bit的编码：' + str(hashCode) + '\n' + bin(hashCode))
    return hashCode


#以下代码段用于函数测试
#readTXTintoJSON("火车站.txt","StationDict.json")
'''
global_dict = readTXTintoPydictwithFreq("火车站.txt")
print("这里打印结果：大黄蜂！！！！！！")
print(selectFromPydict("大黄蜂"))
'''

def init(str):
    global global_dict
    global_dict = readTXTintoPydictwithFreq("SemanticCorrect/火车站.txt")
    # global_dict = readTXTintoPydictwithFreq("/home/ocr/Ocr2/SemanticCorrect/火车站.txt")

    return selectFromPydict(str)


#print(init("长春"))