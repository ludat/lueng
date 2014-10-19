#!/bin/env python3

import threading
import logging

import time
import subprocess
import re

IS_SAFE = True
NAME = 'IP'
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
        IPsRegex = re.compile(
            ("[0-9]*\\.[0-9]*\\.[0-9]*\\.[0-9]*/[0-9]*"),
            re.DOTALL)
        while True:
            IPProc = subprocess.Popen(
                ["ip", "a"],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            IPProc.wait()
            IPOutput = IPProc.stdout.read()
            IPs = IPsRegex.findall(IPOutput)
            result = ""
            for IP in IPs:
                if IP != "127.0.0.1/8":
                    result = IP

            if self.killed():
                break
            self.updateContent(result)
            time.sleep(1)

    def updateContent(self, string):
        if string != self.lastUpdate:
            if string == "":
                try:
                    Proc = subprocess.Popen(
                        ["festival", "--tts"],
                        stdin=subprocess.PIPE,
                        universal_newlines=True)
                    Proc.stdin.write("connection lost")
                    Proc.stdin.close()
                except:
                    pass
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
