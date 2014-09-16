#!/bin/env python3

import threading

import subprocess
import re

IS_SAFE = True
NAME = 'pulseAudioStatus'


class mainThread (threading.Thread):
    def __init__(self, mainQueue, inputQueue=None, logger=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.logger = logger
        self.mainQueue = mainQueue
        self.lastUpdate = "dsadwa"
        self.inputQueue = inputQueue
        self.inputThread = InputThread(self.name, self.inputQueue)
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        if self.inputQueue is not None:
            self.inputThread.start()
        susc = subprocess.Popen(
            ["pactl", "subscribe"],
            stdout=subprocess.PIPE,
            universal_newlines=True)
        stateRegex = re.compile(
            (
                "Mute: (?P<mute>\w+).*?"
                "Volume.*?(?P<left>[0-9]+)%.*?(?P<right>[0-9]+)%.*"
            ),
            re.DOTALL)
        while True:
            if self.killed():
                break
            statusProc = subprocess.Popen(
                ["pactl", "list", "sinks"],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            statusProc.wait()
            statusOutput = statusProc.stdout.read()
            d = stateRegex.search(statusOutput).groupdict()
            if d['mute'] == 'no':
                result = str((int(d['left']) + int(d['left'])) // 2) + "%"
            if d['mute'] == 'yes':
                result = "muted"
            self.updateContent(self.parse(result))
            while True:
                delta = susc.stdout.readline()[:-1].split(" ")
                if delta == ['']:
                    break
                if delta[3] == "sink"and delta[4] == "#0":
                    break
        susc.terminate()
        self.inputThread.kill()
        return 0

    def updateContent(self, string):
        if string != self.lastUpdate:
            self.mainQueue.put({'name': self.name, 'content': string})
            self.lastUpdate = string

    def parse(self, string):
        string = "^ca(1, echo " + self.name + "@clicked)" + string
        string = string + "^ca()"
        return string

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()


class InputThread (threading.Thread):
    def __init__(self, name, inputQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.inputQueue = inputQueue
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        stateRegex = re.compile(
            (
                "Mute: (?P<mute>\w+).*?"
                "Volume.*?(?P<left>[0-9]+)%.*?(?P<right>[0-9]+)%.*"
            ),
            re.DOTALL)
        while True:
            if self.killed():
                break
            item = self.inputQueue.get()
            print("MESSAGE RECIVED:" + item)
            if item == "clicked":
                statusProc = subprocess.Popen(
                    ["pactl", "list", "sinks"],
                    stdout=subprocess.PIPE,
                    universal_newlines=True)
                statusProc.wait()
                statusOutput = statusProc.stdout.read()
                d = stateRegex.search(statusOutput).groupdict()
                if d['mute'] == 'no':
                    s = "1"
                if d['mute'] == 'yes':
                    s = "0"
                resultProc = subprocess.Popen(
                    ["pactl", "set-sink-mute", "0", s])
                resultProc.wait()
        return 0

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    pass
