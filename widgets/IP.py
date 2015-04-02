#!/bin/env python3
import time
import subprocess
import re
import sys

lastUpdate = "dsadwa"
lastIPs = []

def main():
    IPsRegex = re.compile(
        ("[0-9]*\\.[0-9]*\\.[0-9]*\\.[0-9]*/[0-9]*"),
        re.DOTALL)
    global lastIPs
    while True:
        IPOutput = subprocess.check_output(
            ["ip", "a"],
            universal_newlines=True)
        IPs = sorted(IPsRegex.findall(IPOutput))
        if len(IPs) < len(lastIPs):
            shout("connection lost")
        elif len(IPs) > len(lastIPs):
            shout("connection acquired")
        lastIPs = IPs
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
        printContent(string)
        lastUpdate = string

def shout(string):
    try:
        Proc = subprocess.Popen(
            ["festival", "--tts"],
            stdin=subprocess.PIPE,
            universal_newlines=True)
        Proc.stdin.write(string)
        Proc.stdin.close()
    except FileNotFoundError:
        pass


def printContent(string):
    sys.stdout.write(string+"\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
