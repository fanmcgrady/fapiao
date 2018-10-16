import os
import sys
import datetime

class timewatch(object):

    def start(self):
        self.start_time = timewatch.get_time()

    def get_elapsed_time(self):
        current_time = timewatch.get_time()
        res = current_time - self.start_time
        return res

    def get_elapsed_seconds(self):
        elapsed_time = self.get_elapsed_time()
        res = elapsed_time.total_seconds()
        return res

    @staticmethod
    def get_time():
        res = datetime.datetime.now()
        return res

    @staticmethod
    def start_new():
        res = timewatch()
        res.start()
        return res

