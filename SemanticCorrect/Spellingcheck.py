# -*- coding: utf-8 -*-

import time
import os
import sys
import re
import urllib2, urllib
import HTMLParser

reload(sys)
sys.setdefaultencoding('utf-8')


class getGoogleSuggestion:
    def __init__(self):
        self.cx = '012080660999116631289:zlpj9ypbnii'

    def getSuggestion(self, query):
        url = ('http://www.google.com/search?'
               'q=%s'
               '&hl=zh'
               '&output=xml'
               '&client=google-csbe'
               '&cx=%s') % (urllib.quote(query), self.cx)
        request = urllib2.Request(url, None)
        response = urllib2.urlopen(request).read()
        h = HTMLParser.HTMLParser()
        print (h.unescape(response))


if __name__ == '__main__':
    test = getGoogleSuggestion()
    keyword = '为所玉为'
    test.getSuggestion(keyword)