#coding=utf-8

import os
import SemanticCorrect.ComputeDistance as CD
import SemanticCorrect.Porter
import copy

from home import views

#import  from      #字模库 wordTemp
# type:dict   {'一':1.0,'二':0.6}

#import  from      #词库   speechTemp

standardCfdValue = 0.8

def SmtcCrt(sentence , sentenceType , chooseMod):
    #sentence 为list [字，置信度]   {word , confidentValue}
    '''tp = {
    'word': ['一','二'],
    'belief': [0.8,1]
}   '''

    sentenceComb = {
        'porterStr': []
    }

    '''    {
    'porterStr':
            'str':'',
            'belief':[]
         }
    }
    '''
    global standardCfdValue
    #originSent = sentence[:][0]
    '''for index, i in enumerate(sentence):
        #[]
        if i[1] < standardCfdValue:
            wtf = getFamiliar(i[0],index)
            sentenceComb.append(getFamiliar(i[0],index))
        else:
            sentenceComb.append([sentence[index],index])
    
    Result = []
    selectFamiliar(sentence, [], 0, Result)

    for c in Result:
        getWholeConfdt(c)
    '''
    #检测多字
    for index, mm in enumerate(sentence['word']):
        words = ''.join(sentence['word'][:index]+sentence['word'][index+1:])
        sFPCM2 = SemanticCorrect.redict.init(words)

        if sFPCM2 > 0:
            return words


    for index, i in enumerate(sentence['word']):
        if sentence['belief'][index] < standardCfdValue:
            wtf = getFamiliar(i)
            wtfBelief = getBelief(wtf)
            sentenceProduct(sentenceComb, wtf, wtfBelief )
        else:
            sentenceAdd(sentenceComb, sentence['word'][index], sentence['belief'][index])

    '''    'porterStr':[
            {'str':'1','belief':0.8},
            {'str':'2','belief':1}
    ]'''
    print(sentenceComb)

    maxBelief = -1
    iDMAX = -1
    tpPorter = {}

    if chooseMod == 1:

        for indexM, m in enumerate(sentenceComb['porterStr']):

            sFPCM1 = SemanticCorrect.redict.init(m['str'])

            if sFPCM1 > 0:
                return m['str']
                #火车票单个词识别

    longtimeCrtOn = False#关闭长时测试

    if not longtimeCrtOn:
        return ''.join(sentence['word'])



    for indexM, m in enumerate(sentenceComb['porterStr']):

        fp = None
        fp = SemanticCorrect.Porter.porterFront(m['str'],m['belief'])
        print(m['str'])
        print(m['belief'])
        print(fp)
        if fp['belief'] > maxBelief:
            maxBelief = fp['belief']
            iDMAX = indexM
            tpPorter = fp


    print(type(tpPorter))
    print(tpPorter)
    print(sentenceComb['porterStr'][iDMAX]['str'])

    return sentenceComb['porterStr'][iDMAX]['str']


#sentence 为list [字，置信度]   [word , confidentValue]

def getFamiliar(word):
    # dc = CD.load_dict('SemanticCorrect/hei_20.json')  # 取20个形似字
    dc = views.global_dic
    wt = dc[word]
    wt[word] = 1
    #wordTemp接口getFamiliar(word)
    #wordTemp[word] type:dict
    '''wtf = []
    for i in wt:
        wtf.append(i)'''
    return wt
    #list形式
#差近似字形

def getBelief(wtf):
    belief=[]
    for c in wtf:
        #print(c)
        belief.append(wtf[c])

    return belief


'''
def joinSent(listS):
    #组合字串
    str=""
    for i in listS:
        str+=i[0]
    return str
#组合句子


def selectFamiliar(sentence, halfsentence, index, Result):
    #形似字中选取
    global standardCfdValue

    #if index == 0:
    #   halfsentence = []
    #初始化

    if index == len(sentence):
        Result.append(halfsentence)
        #在这里存?
        return None
    #递归结尾

    if sentence[index][1] < standardCfdValue:
        wtf = getFamiliar(sentence[index][0], index)
        for c in wtf:
            halfsentence.append(c)
            #存入句串格式???[word,ocr置信度,字形置信度]
            return halfsentence.append(selectFamiliar(sentence, halfsentence, index+1, Result))

    else:
        halfsentence.append(sentence[index])
        # 存入句串格式???[word,ocr置信度,字形置信度]
        return halfsentence.append(selectFamiliar(sentence, halfsentence, index+1, Result))
#根据预置生成可能句子组合 保存在Result

def getWholeConfdt(sentence):

    return

'''

def sentenceAdd(wordList, word, belief):
    #['wordList': , 'belief': [ , , ]]

    if len(wordList['porterStr']) == 0:

        wordList['porterStr'].append({'str': word, 'belief': [belief]})
        return wordList

    #if len(wordList['porterStr']) == 1:

    for g in wordList['porterStr']:

        g['str'] += word
        g['belief'].append(belief)

    return wordList


def sentenceProduct(wordList, word, belief):

    wLT = copy.deepcopy(wordList)
    #print(wLT)
    if len(wordList['porterStr']) == 0:
        for indexInZ, b in enumerate(word):
            wordList['porterStr'].append({'str': b , 'belief':[belief[indexInZ]]})
        return wordList

    for index, c in enumerate(wLT['porterStr']):
        for indexIn, a in enumerate(word):
            if indexIn == 0:
                wordList['porterStr'][index]['str'] += a
                wordList['porterStr'][index]['belief'].append(belief[indexIn])
            else:
                ctmp = copy.deepcopy(c['belief'])
                ctmp.append(belief[indexIn])
                wordList['porterStr'].append({'str':c['str'] + a, 'belief':ctmp})


    return wordList

'''
def copy_dict(d):
    #深拷贝
    res = {}

    if not d:
        return {}

    for key, value in d.items():
        # 如果不是dict字典，则直接赋值
        if not isinstance(value, dict):
            res[key] = value
        # 如果还是字典，递归调用copy_dict(d)
        else:
            res[key] = copy_dict(value)
    return res
'''
#print(getFamiliar('咱'))
#print(getFamiliar('滨'))
'''
sentence = {
#    'word': ['浙', '江', '省', '绍', '兴', '市'],
        #'word': ['长', '卷', '长', '兴'],
        #'belief': [0.9,0.7,0.9,1.0]
    'word': ['哈', '尔', '滴'],
    'belief': [0.9,0.9,0.4]

#    'belief': [0.9, 0.7, 0.9, 1.0, 1.0, 1.0]
}
print(SmtcCrt(sentence,1))

'''

