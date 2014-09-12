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
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        IPsRegex = re.compile(
            ("[0-9]*\\.[0-9]*\\.[0-9]*\\.[0-9]*/[0-9]*"),
            re.DOTALL)
        while True:
            if self.killed():
                break
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

            self.mainQueue.put({'name': self.name, 'content': result})
            time.sleep(3)

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    pass
