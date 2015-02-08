#!/bin/env python3

import threading
import logging

import time
import subprocess
import re

logger = logging.getLogger('WIDGET')

codeName = 'aaa'
lastUpdate = "dsadwa"

def main():
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
                break
        updateContent(result)
        time.sleep(1)

def updateContent(string):
    global lastUpdate
    if string != lastUpdate:
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
        else:
            try:
                Proc = subprocess.Popen(
                    ["festival", "--tts"],
                    stdin=subprocess.PIPE,
                    universal_newlines=True)
                Proc.stdin.write("connection acquired")
                Proc.stdin.close()
            except:
                pass
        printContent(string)
        lastUpdate = string

def printContent(string):
    print("{}|{}".format(codeName,string))

if __name__ == "__main__":
    main()
