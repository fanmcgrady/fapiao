


class finalPorter:

    porter = {
        'sum': '',
        'belief': '',
        'detailList':[],
    }

    def add(self, sTR, beliefLevel, frequentness):
        tp = {'str': '', 'beliefLevel' : 1, 'frequentness' : 1}

        tp['str'] = sTR
        tp['beliefLevel'] = self.getProduct(beliefLevel)  #list
        tp['frequentness'] = frequentness

        self.porter['detailList'].append(tp)

    def setSum(self,sum):
        self.porter['sum'] = sum

    def getProduct(self,lst):
        sp = 1
        for c in lst:
            sp *= c
        return sp

    def getTotalBelief(self):
        tp = 1
        for c in self.porter['detailList']:

            tp *= float(c['beliefLevel'])
        return tp


    def setBelief(self,sTR):
        temp = 1

        temp *= self.getTotalBelief()
        #temp *=
        temp *= len(sTR) - self.porter['sum']

        self.porter['belief'] = temp