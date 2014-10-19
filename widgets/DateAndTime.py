#!/bin/env python3

import threading
import logging

import time
import datetime

IS_SAFE = True
NAME = 'datetime'
logger = logging.getLogger('WIDGET')


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
        while True:
            now = datetime.datetime.now()
            result = now.strftime("%Y-%m-%d %H:%M:%S")
            if self.killed():
                break
            self.updateContent(result)
            time.sleep(1)
        return 0

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
