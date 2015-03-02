#!/bin/env python3

import socket
import time
import sys


lastUpdate = "dsadwa"

def main():
    while True:
        status = getResultOfCommand("status")
        result = ""
        if 'error' in status:
            result = status['error']
            updateContent(parse(result))
            time.sleep(10)
            result = ""
        elif status['state'] == "stop":
            result = ""
        elif status['state'] == "pause":
            currentSong = getResultOfCommand("currentsong")
            if 'error' in currentSong:
                result = currentSong['error']
            else:
                result = (
                    "^i(icons/xbm/pause.xbm) " +
                    "{}% - {} - {}".format(
                        status['volume'],
                        currentSong['Title'],
                        currentSong['Artist']
                    )
                )
        elif status['state'] == "play":
            currentSong = getResultOfCommand("currentsong")
            if 'error' in currentSong:
                result = currentSong['error']
            else:
                result = (
                    "^i(icons/xbm/play.xbm) " +
                    "{}% - {} - {}".format(
                        status['volume'],
                        currentSong['Title'],
                        currentSong['Artist']
                    )
                )
        else:
            result = "SHIT"

        updateContent(parse(result))
        idle()
    return 0

def idle():
    "Wait until mpd is on and something has happened"
    while True:
        data = None
        try:
            sock = connectTcp('localhost', 6600, timeout=None)
            sock.sendall(bytes("idle\n", encoding="utf-8"))
            data = ""
            while True:
                data = sock.recv(4096).decode("utf-8")
                if data == "" or data.endswith("OK\n"):
                    break
            sock.close()
        except:
            time.sleep(2)
        if data is not None:
            return

def getResultOfCommand(command):
    "Get the result of sending a command to the mpd server"
    data = ""
    try:
        sock = connectTcp('localhost', 6600)
        sock.sendall(bytes(command + "\n", encoding="utf-8"))
        while True:
            data += sock.recv(4096).decode("utf-8")
            if data == "" or data.endswith("OK\n"):
                break
        sock.close()
    except:
        return {'error': 'Connection error'}

    return parseInput(data)

def parseInput(data):
    result = {}
    lines = data.splitlines()
    for line in lines:
        if ": " in line:
            key, content = line.split(": ", 1)
            result[key] = content
    return result

def connectTcp(host, port, timeout=2):
    "Abstraction for tcp connections"
    try:
        flags = socket.AI_ADDRCONFIG
    except AttributeError:
        flags = 0
    err = None
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM, socket.IPPROTO_TCP,
                                  flags):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.settimeout(timeout)
            sock.connect(sa)
            return sock
        except socket.error as e:
            err = e
            if sock is not None:
                sock.close()
    if err is not None:
        raise err
    else:
        raise ConnectionError("getaddrinfo returns an empty list")


def parse(string):
    return string

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
