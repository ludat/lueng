#!/bin/env python3

import threading
import time

import subprocess
import re

IS_SAFE = False
NAME = 'acpiStatus'


class mainThread (threading.Thread):
    def __init__(self, mainQueue, inputQueue=None, logger=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.logger = logger
        self.mainQueue = mainQueue
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        acpisRegex = re.compile(".*?: (.*)")
        while True:
            if self.killed():
                break
            acpiProc = subprocess.Popen(
                ["acpi"],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            acpiProc.wait()
            acpiOutput = acpiProc.stdout.read()
            acpis = acpisRegex.findall(acpiOutput)
            result = acpis[0]
            self.mainQueue.put({'name': self.name, 'content': result})
            time.sleep(3)

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    pass
