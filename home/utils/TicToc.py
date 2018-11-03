import time


class Timer(object):
    def __init__(self):
        self.total_time = 0.
        self.calls = 0
        self.start_time = 0.
        self.diff = 0.
        self.average_time = 0.
        # 一共多少段时间
        self.times = {}
        self.last_time = 0.
        self.current_time = 0.

    def tic(self):
        self.start_time = time.time()

    def toc(self, average=True, content=""):
        self.last_time = self.start_time
        self.current_time = time.time()

        self.diff = round(self.current_time - self.last_time, 2)

        self.last_time = self.current_time

        self.times[content] = self.diff

        self.total_time += self.diff
        self.calls += 1
        self.average_time = self.total_time / self.calls
        if average:
            return self.average_time
        else:
            return self.diff

    def __str__(self):
        text = ""
        index = 1
        for key in self.times:
            text += " " + str(index) + " " + key + "耗时：" + str(self.times[key]) + "s<br>"
            index += 1

        text += "总耗时：" + str(self.total_time) + "s"

        return text
