#!/bin/env python3

import threading
import time

import subprocess
import re

IS_SAFE = True
NAME = 'IP'


class mainThread (threading.Thread):
    def __init__(self, mainQueue, inputQueue=None, logger=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.logger = logger
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
                Proc = subprocess.Popen(
                    ["festival", "--tts"],
                    stdin=subprocess.PIPE,
                    universal_newlines=True)
                Proc.stdin.write("connection lost")
                Proc.stdin.close()
            self.mainQueue.put({'name': self.name, 'content': string})
            self.lastUpdate = string

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    import queue
    import logging

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
        inputQueue=inputQueue,
        logger=logging.getLogger("main"))
    thread.start()
    inputThread.start()

    while True:
        print(mainQueue.get()['content'])
