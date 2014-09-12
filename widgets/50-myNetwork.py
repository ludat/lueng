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
                result = str(((int(d['left']) + int(d['left'])) // 2)) + "%"
            if d['mute'] == 'yes':
                result = "muted"
            self.mainQueue.put({'name': self.name, 'content': result})
            result = ""
            cond = True
            while cond:
                delta = susc.stdout.readline()[:-1].split(" ")
                if delta[3] == "sink"and delta[4] == "#0":
                    cond = False

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    pass
