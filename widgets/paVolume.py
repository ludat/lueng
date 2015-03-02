#!/bin/env python3

import subprocess
import re
import sys


lastUpdate = "dsadwa"

def main():
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
        statusProc = subprocess.Popen(
            ["pactl", "list", "sinks"],
            stdout=subprocess.PIPE,
            universal_newlines=True)
        statusProc.wait()
        statusOutput = statusProc.stdout.read()
        d = stateRegex.search(statusOutput).groupdict()
        if d['mute'] == 'no':
            result = (
                "{}% ".format((int(d['left']) + int(d['left'])) // 2) +
                "^i(icons/xbm/spkr_01.xbm)"
            )
        if d['mute'] == 'yes':
            result = (
                " ^i(icons/xbm/spkr_02.xbm)"
            )
        updateContent(parse(result))
        while True:
            delta = susc.stdout.readline()[:-1].split(" ")
            if delta == ['']:
                break
            if delta[3] == "sink"and delta[4] == "#0":
                break
    susc.terminate()
    return 0

def parse(string):
    return "^ca(1, pactl set-sink-mute 0 toggle)" + string + "^ca()"

def updateContent(string):
    global lastUpdate
    if string != lastUpdate:
        printContent(string)
        lastUpdate = string

def printContent(string):
    sys.stdout.write(string+"\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
