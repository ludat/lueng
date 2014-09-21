#!/bin/env python3

import threading

import subprocess
import re

IS_SAFE = False
NAME = 'pulseAudioStatus'


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
        susc = subprocess.Popen(
            ["pactl", "subscribe"],
            stdout=subprocess.PIPE,
            universal_newlines=True)
        stateRegex = re.compile(
            (
                "Mute: (?P<mute>\w+).*?"
                "Volume.*?(?P<left>[0-9]+)%.*?"
                "(?P<right>[0-9]+)%.*"
            ),
            re.DOTALL)
        result = ""
        while True:
            statusProc = subprocess.Popen(
                ["pactl", "list", "sinks"],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            statusProc.wait()
            statusOutput = statusProc.stdout.read()
            d = stateRegex.search(statusOutput).groupdict()
            if d['mute'] == 'no':
                result = str(((int(d['left']) + int(d['left'])) // 2)) + "%"
            if d['mute'] == 'yes':
                result = "muted"
            if self.killed():
                break
            self.updateContent(result)
            result = ""
            cond = True
            while cond:
                delta = susc.stdout.readline()[:-1].split(" ")
                if delta[3] == "sink"and delta[4] == "#0":
                    cond = False

    def updateContent(self, string):
        if string != self.lastUpdate:
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
