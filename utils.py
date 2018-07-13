import threading
import time


_timers = {}
class DiscreteEventEmitter():
    '''
    A slightly modified version of the otree-redwood DiscreteEventEmitter

    The only difference is that in this version, the callback is called as soon as the timer is started,
    rather than after a 1-interval delay
    '''

    def __init__(self, interval, period_length, group, callback):
        self.interval = float(interval)
        self.period_length = period_length
        self.group = group
        self.intervals = self.period_length / self.interval
        self.callback = callback
        self.current_interval = 0

    def _tick(self):
        start = time.time()
        self.callback(self.current_interval, self.intervals)
        self.current_interval += 1
        if self.current_interval < self.intervals:
            self.timer = threading.Timer(self._time, self._tick)
            _timers[self.group] = self.timer
            self.timer.start()
    
    @property
    def _time(self):
        return self.interval - ((time.time() - self.start_time) % self.interval)

    def start(self):
        self.start_time = time.time()
        self._tick()

    def stop(self):
        del _timers[self.group]