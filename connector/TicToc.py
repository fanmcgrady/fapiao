import time

# 计时器
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

    def tic(self):
        current_time = time.time()
        self.start_time = current_time

        self.last_time = current_time

    def toc(self, average=True, content=""):
        current_time = time.time()

        self.diff = round(current_time - self.last_time, 2)

        self.last_time = current_time

        # 缩短不该计算的耗时
        if content == '行提取图绘制' and self.diff > 0.1:
            self.diff = round(self.diff - 0.1, 2)

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
            text += " " + str(index) + ": " + key + "耗时：" + str(self.times[key]) + "s<br>"
            index += 1

        text += "总耗时：" + str(round(self.total_time, 2)) + "s"

        return text
