#!/bin/env python3

import threading

from time import sleep
import re
import subprocess

IS_SAFE = True
NAME = 'ramStatus'
WIDTH = 70


class mainThread (threading.Thread):
    def __init__(self, mainQueue, inputQueue=None, logger=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.logger = logger
        self.mainQueue = mainQueue
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        freeRegex = re.compile("Mem: *(?P<total>[0-9]+).*?cache: *(?P<used>[0-9]+) *(?P<free>[0-9]+)", re.DOTALL)
        while True:
            if self.killed():
                break
            freeProc = subprocess.Popen(["free"], stdout=subprocess.PIPE, universal_newlines=True)
            freeProc.wait()
            freeOutput = freeProc.stdout.read()
            d = freeRegex.search(freeOutput).groupdict()
            result = self.format(d)
            self.mainQueue.put({'name':self.name, 'content':result})
            sleep(1)
        return 0

    def format(self, d):
        string = ""
        for k in d:
            d[k] = int(d[k])

        used = round( d['used'] * WIDTH / d['total'] )
        free = round( d['free'] * WIDTH / d['total'] )

        return ("^fg(#CCCCCC)^r({}x1)^fg(#999999)^r({}x1)^fg()".format(used, free))

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    pass
