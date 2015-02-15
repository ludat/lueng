#!/bin/env python3

import time
import datetime

lastUpdate = "dsadwa"

def main():
    while True:
        now = datetime.datetime.now()
        result = now.strftime("%Y-%m-%d %H:%M:%S")
        updateContent(result)
        time.sleep(1)
    return 0

def updateContent(string):
    global lastUpdate
    if string != lastUpdate:
        printContent(string)
        lastUpdate = string

def printContent(string):
    print(string)

if __name__ == "__main__":
    main()
