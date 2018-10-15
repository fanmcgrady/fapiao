import os
import json
import copy
import SemanticCorrect.redict


# import SemanticCorrect.fPter


class finalPorter:
    porter = {
        'sum': '',
        'belief': '',
        'detailList': [],
    }

    def __init__(self):
        self.porter = {
            'sum': '',
            'belief': '',
            'detailList': [],
        }

    def add(self, sTR, beliefLevel, frequentness):
        tp = {'str': '', 'beliefLevel': 1, 'frequentness': 1}

        tp['str'] = sTR
        tp['beliefLevel'] = self.getProduct(beliefLevel)  # list
        tp['frequentness'] = frequentness

        self.porter['detailList'].append(tp)

    def setSum(self, sum):
        self.porter['sum'] = sum

    def getProduct(self, lst):
        sp = 1
        for c in lst:
            sp *= c
        return sp

    def getTotalBelief(self):
        tp = 1
        for c in self.porter['detailList']:
            tp *= float(c['beliefLevel'])
        return tp

    def setBelief(self, sTR):
        temp = 1

        temp *= self.getTotalBelief()
        # temp *=
        temp *= len(sTR) - self.porter['sum']

        self.porter['belief'] = temp


def porterFront(sTR, beliefLevel):
    # 前向分词
    # return list [[' ',频度],[' ',频度]...]   no.len(list)

    i = 0
    fp = finalPorter()
    strTemp = copy.deepcopy(sTR)
    beliefLevelTemp = copy.deepcopy(beliefLevel)

    while len(strTemp) > 0:
        i += 1
        if len(strTemp) == 1:
            fp.add(strTemp[0:1], beliefLevelTemp[0:1], 10)
            strTemp = ''
            # 单字

        for a in range(0, len(strTemp)):
            # print('in'+str(a))
            if a == len(strTemp) - 1:
                fp.add(strTemp[0:1], beliefLevelTemp[0:1], 10)
                strTemp = copy.deepcopy(strTemp[1:len(strTemp)])
                beliefLevelTemp = copy.deepcopy(beliefLevelTemp[1:len(strTemp)])
                # 单字
                break

            sFP = SemanticCorrect.redict.init(strTemp[0:len(strTemp) - a])
            if sFP > 0:
                fp.add(strTemp[0:len(strTemp) - a], beliefLevelTemp[0:len(strTemp) - a], sFP)
                # fp.add(strTemp[0:a], beliefLevelTemp[0:a], getPhrases(strTemp[0:a]))
                strTemp = copy.deepcopy(strTemp[len(strTemp) - a:len(strTemp)])
                beliefLevelTemp = copy.deepcopy(beliefLevelTemp[len(strTemp) - a:len(strTemp)])
                break

    fp.setSum(i)
    fp.setBelief(sTR)

    return fp.porter


def FrtPtr(substr):
    return


def init():
    str1 = {
        'str': '长春长兴',
        'belief': [0.9, 0.7, 0.9, 1.0]

    }
    ftp = porterFront(str1['str'], str1['belief'])
    print(ftp)


def FuzzyPorterFront(sTR, beliefLevel):
    # 替换一位

    fp = finalPorter()
    strTemp = copy.deepcopy(sTR)
    beliefLevelTemp = copy.deepcopy(beliefLevel)


# init()



'''
str1={
        'str': '长春长兴',
        'belief': [0.9,0.7,0.9,1.0]

}
ftp= porterFront(str1['str'],str1['belief'])
print(ftp)
'''
