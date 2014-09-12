#!/bin/env python3

import threading

from time import sleep
import datetime

IS_SAFE = True
NAME = 'datetime'


class mainThread (threading.Thread):
    def __init__(self, mainQueue, inputQueue=None, logger=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.logger = logger
        self.mainQueue = mainQueue
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        while True:
            if self.killed():
                break
            now = datetime.datetime.now()
            result = now.strftime("%Y-%m-%d %H:%M:%S")
            self.mainQueue.put({'name': self.name, 'content': result})
            sleep(1)
        return 0

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    pass
