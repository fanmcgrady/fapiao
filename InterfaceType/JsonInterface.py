import json
import os
'''
class TrainCard:                     #火车票
        dic = {
                'returnStateInfo':{
                    'returnCode':'',#返回代码
                    'returnMessage':''#返回描述
                },
                'TrainCard':{
                    'Earmarkedinvoice': '',
                    'Finalstation': '',
                    'TrainNum': '',
                    'Date': '',
                    'Money': '',
                    'Seatnum': '',
                    'name': '',
                    'identity': '',
                    'Ticketnum': ''
                }
        }
        def __init__(self,Earmarkedinvoice,Finalstation,TrainNum,Date,Money,Seatnum,name,identity,Ticketnum,returnCode,returnMessage): #始发站，终到站，车次，日期，金额，座位号，姓名，身份证号，车票序号
            self.dic['TrainCard']['Earmarkedinvoice']=Earmarkedinvoice
            self.dic['TrainCard']['Finalstation'] = Finalstation
            self.dic['TrainCard']['TrainNum'] = TrainNum
            self.dic['TrainCard']['Date'] = Date
            self.dic['TrainCard']['Money'] = Money
            self.dic['TrainCard']['Seatnum'] = Seatnum
            self.dic['TrainCard']['name'] = name
            self.dic['TrainCard']['identity'] = identity
            self.dic['TrainCard']['Ticketnum'] = Ticketnum
            self.dic['returnStateInfo']['returnCode'] = returnCode
            self.dic['returnStateInfo']['returnMessage'] = returnMessage
        def toJson(self,filename,name):                                    #filename是存储地址，name是存储名
            with open(os.path.join(filename,name+'.json'),'w', encoding='utf-8') as json_file:
                json.dump(self.dic, json_file, ensure_ascii=False)

class SpecialInvoice:               #专用发票
    dic = {
            'returnStateInfo':{
                'returnCode':'',#返回代码
                'returnMessage':''#返回描述
                },
            'SpecialInvoice':{
                'InvoiceAci': '',
                'InvoiceNum': '',
                'InvoiceDate': '',
                'Money': '',
                'Tax': '',
                'AllMoney': '',
                'BuyerName': '',
                'BuyerIdentNum': '',
                'SalerName': '',
                'SalerIdentNum':''
                }
    }

    def __init__(self, InvoiceAci, InvoiceNum, InvoiceDate, Money, Tax, AllMoney, BuyerName, BuyerIdentNum, SalerName, SalerIdentNum, returnCode, returnMessage ):  # 发票代码，发票号码，开票日期，金额，税额，价税合计，购买方名称，购买方纳税人识别号，销售方名称，销售方纳税人识别号
        self.dic['SpecialInvoice']['InvoiceAci'] = InvoiceAci
        self.dic['SpecialInvoice']['InvoiceNum'] = InvoiceNum
        self.dic['SpecialInvoice']['Money'] = Money
        self.dic['SpecialInvoice']['Tax'] = Tax
        self.dic['SpecialInvoice']['Money'] = Money
        self.dic['SpecialInvoice']['InvoiceDate'] = InvoiceDate
        self.dic['SpecialInvoice']['AllMoney'] = AllMoney
        self.dic['SpecialInvoice']['BuyerName'] = BuyerName
        self.dic['SpecialInvoice']['BuyerIdentNum'] = BuyerIdentNum
        self.dic['SpecialInvoice']['SalerName'] = SalerName
        self.dic['SpecialInvoice']['SalerIdentNum'] = SalerIdentNum
        self.dic['returnStateInfo']['returnCode'] = returnCode
        self.dic['returnStateInfo']['returnMessage'] = returnMessage
    def toJson(self, filename, name):  # filename是存储地址，name是存储名
        with open(os.path.join(filename, name + '.json'), 'w', encoding='utf-8') as json_file:
            json.dump(self.dic, json_file, ensure_ascii=False)

class CommonInvoice:            #普通发票
    dic = {
            'returnStateInfo':{
                'returnCode':'',#返回代码
                'returnMessage':''#返回描述
                },
            'CommonInvoice':{
                'InvoiceAci': '',
                'InvoiceNum': '',
                'InvoiceDate': '',
                'Money': '',
                'Tax': '',
                'AllMoney': '',
                'BuyerName': '',
                'BuyerIdentNum': '',
                'SalerName': '',
                'SalerIdentNum': '',
                'VerificationAci': ''
            }
    }

    def __init__(self, InvoiceAci, InvoiceNum, InvoiceDate, Money, Tax, AllMoney, BuyerName, BuyerIdentNum, SalerName,SalerIdentNum,VerificationAci,returnCode,returnMessage):  # 发票代码，发票号码，开票日期，金额，税额，价税合计，购买方名称，购买方纳税人识别号，销售方名称，销售方纳税人识别号，校验码
        self.dic['InvoiceAci'] = InvoiceAci
        self.dic['InvoiceNum'] = InvoiceNum
        self.dic['Money'] = Money
        self.dic['Tax'] = Tax
        self.dic['Money'] = Money
        self.dic['InvoiceDate'] = InvoiceDate
        self.dic['AllMoney'] = AllMoney
        self.dic['BuyerName'] = BuyerName
        self.dic['BuyerIdentNum'] = BuyerIdentNum
        self.dic['SalerName'] = SalerName
        self.dic['SalerIdentNum'] = SalerIdentNum
        self.dic['VerificationAci'] = VerificationAci
        self.dic['returnStateInfo']['returnCode'] = returnCode
        self.dic['returnStateInfo']['returnMessage'] = returnMessage

    def toJson(self, filename, name):  # filename是存储地址，name是存储名
        with open(os.path.join(filename, name + '.json'), 'w', encoding='utf-8') as json_file:
            json.dump(self.dic, json_file, ensure_ascii=False)
'''
class invoice():


    dic = {
        'returnStateInfo':
            {
                'returnCode': '',#"返回代码"
                'returnMessage': ''#"base64 返回描述"
            },

        'invoice':
            {
                'invoiceType': '',
                'checkState': '',
                'isEInvoice': '',
                'invoiceCode': '',
                'invoiceNo': '',
                'buyerName': '',
                'buyerTaxNo': '',
                'buyerAddress': '',
                'buyerAcount': '',
                'salerName': '',
                'salerTaxNo': '',
                'salerAddress': '',
                'salerAcount': '',
                'invoiceDate': '',
                'verifyCode': '',
                'invoiceAmount': '',
                'taxAmount': '',
                'totalAmount': '',
                'remark': '',
                'invoiceStatus': '',
                'departCity': '',
                'arriveCity': '',
                'trainNumber': '',
                'passenger': '',
                'seatNum': '',
                'idNum': '',
                'ticketsNum': '',
                'detailList': [
                    {
                        'detailNo': '',
                        'goodName': '',
                        'model': '',
                        'unit': '',
                        'num': '',
                        'unitPrice': '',
                        'detailAmount': '',
                        'taxRate': '',
                        'taxAmount': ''
                    }
                ]
            }
    }
    #list.append()
    '''                {
                        'detailNo': '',
                        'goodName': '',
                        'model': '',
                        'unit': '',
                        'num': '',
                        'unitPrice': '',
                        'detailAmount': '',
                        'taxRate': '',
                        'taxAmount': ''
                    }
    '''
    def __init__(self):
        self.dic['invoice'] ={
                'invoiceType': '',
                'checkState': '',
                'isEInvoice': '',
                'invoiceCode': '',
                'invoiceNo': '',
                'buyerName': '',
                'buyerTaxNo': '',
                'buyerAddress': '',
                'buyerAcount': '',
                'salerName': '',
                'salerTaxNo': '',
                'salerAddress': '',
                'salerAcount': '',
                'invoiceDate': '',
                'verifyCode': '',
                'invoiceAmount': '',
                'taxAmount': '',
                'totalAmount': '',
                'remark': '',
                'invoiceStatus': '',
                'departCity': '',
                'arriveCity': '',
                'trainNumber': '',
                'passenger': '',
                'seatNum': '',
                'idNum': '',
                'ticketsNum': '',
                'detailList': [
                    {
                        'detailNo': '',
                        'goodName': '',
                        'model': '',
                        'unit': '',
                        'num': '',
                        'unitPrice': '',
                        'detailAmount': '',
                        'taxRate': '',
                        'taxAmount': ''
                    }
                ]
        }
        self.dic['returnStateInfo'] = {
                'returnCode': '',#"返回代码"
                'returnMessage': ''#"base64 返回描述"
            }

    def addTrainCardInfo(self, departCity, arriveCity, trainNumber, Date, Money, Seatnum, name, idNum, Ticketnum, returnCode, returnMessage):
        self.dic['invoice']['departCity'] = departCity
        self.dic['invoice']['arriveCity'] = arriveCity
        self.dic['invoice']['trainNumber'] = trainNumber
        self.dic['invoice']['passenger'] = name
        self.dic['invoice']['invoiceDate'] = Date
        self.dic['invoice']['totalAmount'] = Money

        self.dic['invoice']['seatNum'] = Seatnum
        self.dic['invoice']['idNum'] = idNum
        self.dic['invoice']['ticketsNum'] = Ticketnum
        self.dic['returnStateInfo']['returnCode'] = returnCode
        self.dic['returnStateInfo']['returnMessage'] = returnMessage
        # 始发站，终到站，车次，日期，金额，座位号，姓名，身份证号，车票序号


    def apdDetail(self,detailNo,goodName,model,unit,num,unitPrice,detailAmount,taxRate,taxAmount):
        detailItem = {
            'detailNo': detailNo,
            'goodName': goodName,
            'model': model,
            'unit': unit,
            'num': num,
            'unitPrice': unitPrice,
            'detailAmount': detailAmount,
            'taxRate': taxRate,
            'taxAmount': taxAmount
        }

        self.dic['invoice']['detailList'].apppend(detailItem)

    def setValueWithDict(self, dict):
        for c in dict:
           self.dic['invoice'][c] = dict[c]

#jss = json.dumps(invoice.dic)
#print(jss)
