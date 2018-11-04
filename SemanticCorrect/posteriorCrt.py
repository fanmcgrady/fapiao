import SemanticCorrect.Porter
import SemanticCorrect.SmtcCrt
import copy


class posteriorCrt():
    dic = {
        'idNum': '',  # 身份证号
        'trainNumber': '',  # 车次号 (D G C)

        'invoiceDate': '',  # 日期
        'seatNum': '',  # 座位号  (**车***号)
        'passenger': '',  # 姓+...
        'departCity': '',  # 出发地
        'arriveCity': '',  # 到达地
        'totalAmount': '',
        'ticketsNum': ''
    }

    VATdic = {
        'invoiceCode': '',  # 发票代码
        'invoiceNo': '',  # 发票号码
        'invoiceDate': '',  # 发票日期
        'invoiceAmount': '',  # 不含税金额
        'totalAmount': ''  # 总金额
    }

    def __init__(self):
        self.dic['idNum'] = ''
        self.dic['trainNumber'] = ''
        self.dic['invoiceDate'] = ''
        self.dic['seatNum'] = ''
        self.dic['passenger'] = ''
        self.dic['departCity'] = ''
        self.dic['arriveCity'] = ''
        self.dic['ticketsNum'] = ''
        self.dic['totalAmount'] = ''

        self.VATdic['invoiceCode'] = ''
        self.VATdic['invoiceNo'] = ''
        self.VATdic['invoiceDate'] = ''
        self.VATdic['invoiceAmount'] = ''
        self.VATdic['totalAmount'] = ''


    def setTrainTicketPara(self, departCity, arriveCity, trainNumber, invoiceDate, seatNum, idNum, passenger,
                           totalAmount):
        self.dic['departCity'] = departCity
        self.dic['arriveCity'] = arriveCity
        self.dic['trainNumber'] = trainNumber
        self.dic['invoiceDate'] = invoiceDate
        self.dic['seatNum'] = seatNum
        self.dic['idNum'] = idNum
        self.dic['passenger'] = passenger
        self.dic['totalAmount'] = totalAmount

    def setTrainTicketParaFromDict(self, dict):
        for c in dict:
            self.dic[c] = dict[c]

    def setVATParaFromVATDict(self, VATdict):
        for c in VATdict:
            self.VATdic[c] = VATdict[c]

    def startTrainTicketCrt(self):

        # 去除起点终点的除汉字外的词  :需要分词 ∴都是汉字
        dc1 = ''
        for c in self.dic['departCity']:
            if self.isChinese(c):
                dc1 += c
        self.dic['departCity'] = dc1

        ac1 = ''
        for c in self.dic['arriveCity']:
            if self.isChinese(c):
                ac1 += c
        self.dic['arriveCity'] = ac1

        # 分词去除站字
        if len(self.dic['arriveCity']) > 0:
            if self.dic['arriveCity'][len(self.dic['arriveCity']) - 1] == '站':
                lf = copy.deepcopy(self.dic['arriveCity'][0:len(self.dic['arriveCity']) - 1])
                self.dic['arriveCity'] = lf

        if len(self.dic['departCity']) > 0:
            if self.dic['departCity'][len(self.dic['departCity']) - 1] == '站':
                lf = copy.deepcopy(self.dic['departCity'][0:len(self.dic['departCity']) - 1])
                self.dic['departCity'] = lf

        if self.dic['departCity'] != '':
            print(self.dic['departCity'])
            self.dic['departCity'] = self.startPorter(self.dic['departCity'])
            print(self.dic['departCity'])

        if self.dic['arriveCity'] != '':
            print(self.dic['arriveCity'])
            self.dic['arriveCity'] = self.startPorter(self.dic['arriveCity'])
            print(self.dic['arriveCity'])

        if len(self.dic['invoiceDate']) > 10:

            for index, x in enumerate(self.dic['invoiceDate']):
                if x == '开':
                    self.dic['invoiceDate'] = self.dic['invoiceDate'][:index + 1]
                    break
            if self.isChinese(self.dic['invoiceDate'][4]):
                self.dic['invoiceDate'] = self.dic['invoiceDate'][0:4] + '年' + self.dic['invoiceDate'][5:]

            if self.isChinese(self.dic['invoiceDate'][7]):
                self.dic['invoiceDate'] = self.dic['invoiceDate'][0:7] + '月' + self.dic['invoiceDate'][8:]

            if self.isChinese(self.dic['invoiceDate'][10]):
                self.dic['invoiceDate'] = self.dic['invoiceDate'][0:10] + '日' + self.dic['invoiceDate'][11:]

        if len(self.dic['seatNum']) > 6:

            self.dic['seatNum'] = self.dic['seatNum'][0:2] + '车' + self.dic['seatNum'][3:]

            if self.isChinese(self.dic['seatNum'][6]):
                self.dic['seatNum'] = self.dic['seatNum'][0:6] + '号'

        idnum = ''
        if len(self.dic['idNum']) != 0:
            for c in self.dic['idNum']:
                if c.isdigit() or c == '*' or c == 'X':
                    idnum += c
            self.dic['idNum'] = idnum
            print(idnum)

            if len(self.dic['idNum']) != 18:
                if self.dic['idNum'][0:10].isdigit() and self.dic['idNum'][len(self.dic['idNum']) - 4:len(
                        self.dic['idNum']) - 1].isdigit():
                    self.dic['idNum'] = self.dic['idNum'][0:10] + '****' + self.dic['idNum'][
                                                                           len(self.dic['idNum']) - 4:len(
                                                                               self.dic['idNum'])]
                print("idNum error")
        else:
            print("idNum doesn't exist!")

        # price
        if len(self.dic['totalAmount']) > 2:
            for index, x in enumerate(self.dic['totalAmount']):
                if x == '元':
                    self.dic['totalAmount'] = self.dic['totalAmount'][:index + 1]
                    break

            if self.dic['totalAmount'][0] != '¥':
                self.dic['totalAmount'] = '¥' + self.dic['totalAmount'][1:]

            if self.dic['totalAmount'][len(self.dic['totalAmount']) - 1] != '元':
                if self.isChinese(self.dic['totalAmount'][len(self.dic['totalAmount']) - 1]):  # ‘元’识别错误
                    self.dic['totalAmount'] = self.dic['totalAmount'][0:len(self.dic['totalAmount']) - 1] + '元'
                if self.dic['totalAmount'][len(self.dic['totalAmount']) - 1].isdigit():  # ‘元’漏
                    self.dic['totalAmount'] = self.dic['totalAmount'] + '元'

            if self.dic['totalAmount'][len(self.dic['totalAmount']) - 3].isdigit():
                self.dic['totalAmount'] = self.dic['totalAmount'][0:len(self.dic['totalAmount']) - 3] + '.' + self.dic[
                                                                                                                  'totalAmount'][
                                                                                                              len(
                                                                                                                  self.dic[
                                                                                                                      'totalAmount']) - 2:len(
                                                                                                                  self.dic[
                                                                                                                      'totalAmount'])]

        # self.dic['passenger  待定
        pger = ''
        for c in self.dic['passenger']:
            if self.isChinese(c):
                pger += c
        self.dic['passenger'] = pger

        tNum = ''
        for c in self.dic['ticketsNum']:
            if not self.isChinese(c):
                tNum += c
        self.dic['ticketsNum'] = tNum

    def isChinese(self, char):
        for ch in char:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
            else:
                return False

    def startPorter(self, Para):
        BeliefL = []
        for c in Para:
            BeliefL.append(1.0)
        pt = SemanticCorrect.Porter.porterFront(Para, BeliefL)

        if pt['sum'] == 1:
            return Para

        i = 0
        lowCount = 0
        for index, a in enumerate(pt['detailList']):
            if len(a['str']) == 1:
                BeliefL[i] = 0.6
                i += 1
                lowCount += 1
            else:
                BeliefL[i] = 0.6
                BeliefL[i + len(a['str']) - 1] = 0.6
                i += len(a['str'])
                if index != len(pt['detailList']) - 1:
                    lowCount += 2
                else:
                    lowCount += 1
        print('lowCount: ' + str(lowCount))
        # 速度控制-------- ------
        if lowCount > 3:
            return Para

        tp = {}
        wordA = []

        for b in Para:
            wordA.append(b)
        tp['word'] = wordA
        tp['belief'] = BeliefL

        print(tp)
        ptC = SemanticCorrect.SmtcCrt.SmtcCrt(tp, 1, 1)  # type=1 地点

        return ptC

    def startFuzzyPorter(self, Para):
        BeliefL = []
        for c in Para:
            BeliefL.append(1.0)
        pt = SemanticCorrect.Porter.porterFront(Para, BeliefL)

        if pt['sum'] == 1:
            return Para

        i = 0

        for index, a in enumerate(pt['detailList']):
            if len(a['str']) == 1:
                BeliefL[i] = 0.6
                i += 1

            else:
                BeliefL[i] = 0.6
                BeliefL[i + len(a['str']) - 1] = 0.6
                i += len(a['str'])

        tp = {}
        wordA = []

        for b in Para:
            wordA.append(b)
        tp['word'] = wordA
        tp['belief'] = BeliefL

        print(tp)
        ptC = SemanticCorrect.SmtcCrt.FuzzyCrt(tp, 1, 1)  # type=1 地点

        return ptC

    def startVATCrt(self):

        # 检测总金额
        # 先取数字串，再格式
        if self.VATdic['totalAmount'] != '' and self.VATdic['totalAmount'].find('.', 0) < 0:
            digitStr = ''
            for c in self.VATdic['totalAmount']:
                if c.isdigit():
                    digitStr += c

            if len(digitStr) > 2:
                self.VATdic['totalAmount'] = '¥' + digitStr[:2] + '.' + digitStr[-2:]
            else:
                print('总金额解析错误！')

        # 检测不含税金额
        # 先取数字串，再格式
        if self.VATdic['invoiceAmount'] != '' and self.VATdic['invoiceAmount'].find('.', 0) < 0:
            digitStr = ''
            for c in self.VATdic['invoiceAmount']:
                if c.isdigit():
                    digitStr += c

            if len(digitStr) > 2:
                self.VATdic['invoiceAmount'] = '¥' + digitStr[:2] + '.' + digitStr[-2:]
            else:
                print('不含税金额解析错误！')

        #发票日期
        digitStrDate = ''
        if len(self.VATdic['invoiceAmount']) >= 8:
            for c in self.VATdic['invoiceDate']:
                if c.isdigit():
                    digitStrDate += c

            if len(digitStrDate) == 8:
                self.VATdic['invoiceDate'] = digitStrDate[:4] + '年' + digitStrDate[4:6] + '月' + digitStrDate[6:] + '日'


        # 发票代码
        digitStrCode = ''
        for c in self.VATdic['invoiceCode']:
            if c.isdigit():
                digitStrCode += c

        if len(digitStrCode) > 10:
            self.VATdic['invoiceCode'] = digitStrCode[:10]

        # 发票号码
        # 修正误识汉字
        digitStrNo = ''
        for c in self.VATdic['invoiceNo']:
            if c.isdigit():
                digitStrNo += c

        if len(digitStrNo) > 8:
            self.VATdic['invoiceNo'] = digitStrNo[-8:]




def init():
    pC = posteriorCrt()
    l = pC.startPorter('咱尔滨')
    print(l)


'''pC = posteriorCrt()
l = pC.startPorter('一哈尔滨长春')
print(l)'''

'''sp = posteriorCrt()
sp.setTrainTicketPara('', '', '', '', '', '', '','¥20.1')
sp.startTrainTicketCrt()
print(sp.dic)'''
