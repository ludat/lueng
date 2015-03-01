#!/bin/env python3

import sys

from time import sleep
import re

WIDTH = 80
lastUpdate = "dsadwa"
memRegex = re.compile(
    (
        '(.*?):\D*?(\d+)\D*'
    ),
    re.DOTALL)


def main():
        while True:
            memFile = open("/proc/meminfo")
            memRaw = memFile.read()
            memDict = parseMemFile(memRaw)
            result = format(memDict)
            updateContent(result)
            sleep(1)
        return 0

def format(d):
    for k in d:
        d[k] = int(d[k])

    free = round(d['MemAvailable'] * WIDTH / d['MemTotal'])
    used = round((d['MemTotal'] - d['MemAvailable'] ) * WIDTH / d['MemTotal'])

    return (
        "^i(icons/xbm/mem.xbm) "
        "^fg(#CCCCCC)^r({}x1)^fg(#999999)^r({}x1)^fg()".format(used, free)
    )

def parseMemFile(raw):
    memArr = raw.splitlines()
    memDict = {}
    for field in memArr:
        key, value = memRegex.search(field).groups()
        memDict[key] = value
    return memDict

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
