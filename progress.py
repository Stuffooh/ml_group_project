from time import time

class ProgressBar:
    def __init__(self, end, bars=50, decimals=1):
        self.end = end
        self.bars = bars
        self.decimals = decimals
        self.start_time = time()

    def format_time(self, time):
        time_str = ""
        parts = ((60, 's'), (60, 'm'), (24, 'D'))
        for t, s in parts:
            time, v = time // t, int(time % t)
            if v == 0:
                continue
            time_str = f'{v}{s} {time_str}'
        return time_str

    def update(self, value):
        assert value >= 0, "Must be larger than 0"
        k = value / self.end
        if k == 0:
            remain_time = 'nan'
        else:
            remain_time = self.format_time((1-k) / k * (time() - self.start_time))
        percent = round(100 * k, self.decimals)
        bars = int(self.bars * k)
        progress = "|" * bars + " " * (self.bars - bars)
        print(f"\r({progress}) {percent}% ~ {remain_time}", end="", flush=True) 
        if value >= self.end:
            print('')
