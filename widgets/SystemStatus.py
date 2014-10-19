#!/bin/env python3

import threading
import logging

from time import sleep
import re
import subprocess

IS_SAFE = True
NAME = 'ramStatus'
logger = logging.getLogger('WIDGET')
WIDTH = 70


class mainThread (threading.Thread):
    def __init__(self, codeName, mainQueue, inputQueue=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.codeName = codeName
        self.mainQueue = mainQueue
        self.lastUpdate = "dsadwa"
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        freeRegex = re.compile(
            (
                "Mem: *(?P<total>[0-9]+).*?"
                "cache: *(?P<used>[0-9]+) *(?P<free>[0-9]+)"
            ),
            re.DOTALL)
        while True:
            freeProc = subprocess.Popen(
                ["free"],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            freeProc.wait()
            freeOutput = freeProc.stdout.read()
            d = freeRegex.search(freeOutput).groupdict()
            result = self.format(d)
            if self.killed():
                break
            self.updateContent(result)
            sleep(1)
        return 0

    def updateContent(self, string):
        if string != self.lastUpdate:
            self.mainQueue.put({
                'name': self.name,
                'codeName': self.codeName,
                'content': string})
            self.lastUpdate = string

    def format(self, d):
        for k in d:
            d[k] = int(d[k])

        used = round(d['used'] * WIDTH / d['total'])
        free = round(d['free'] * WIDTH / d['total'])

        return (
            "^i(icons/xbm/mem.xbm) "
            "^fg(#CCCCCC)^r({}x1)^fg(#999999)^r({}x1)^fg()".format(used, free)
        )

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    import queue

    class TestInputThread(threading.Thread):
        def __init__(self, inputQueue):
            threading.Thread.__init__(self)
            self.inputQueue = inputQueue

        def run(self):
            while True:
                self.inputQueue.put(input())

    inputQueue = queue.Queue()
    mainQueue = queue.Queue()

    inputThread = TestInputThread(inputQueue)

    thread = mainThread(
        mainQueue,
        inputQueue=inputQueue)
    thread.start()
    inputThread.start()

    while True:
        print(mainQueue.get()['content'])
