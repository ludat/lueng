#!/bin/env python3

import threading
import logging

from time import sleep
import re

IS_SAFE = True
NAME = 'ramStatus'
logger = logging.getLogger('WIDGET')
WIDTH = 80


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
        self.memRegex = re.compile(
            (
                '(.*?):\D*?(\d+)\D*'
            ),
            re.DOTALL)
        while True:
            memFile = open("/proc/meminfo")
            memRaw = memFile.read()
            memDict = self.parseMemFile(memRaw)
            result = self.format(memDict)
            if self.killed():
                break
            self.updateContent(result)
            sleep(1)
        return 0

    def format(self, d):
        for k in d:
            d[k] = int(d[k])

        free = round(d['MemAvailable'] * WIDTH / d['MemTotal'])
        used = round((d['MemTotal'] - d['MemAvailable'] ) * WIDTH / d['MemTotal'])

        return (
            "^i(icons/xbm/mem.xbm) "
            "^fg(#CCCCCC)^r({}x1)^fg(#999999)^r({}x1)^fg()".format(used, free)
        )

    def parseMemFile(self, raw):
        memArr = raw.splitlines()
        memDict = {}
        for field in memArr:
            key, value = self.memRegex.search(field).groups()
            memDict[key] = value
        return memDict

    def updateContent(self, string):
        if string != self.lastUpdate:
            self.mainQueue.put({
                'name': self.name,
                'codeName': self.codeName,
                'content': string})
            self.lastUpdate = string

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
