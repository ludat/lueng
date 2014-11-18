#!/bin/env python3

import threading
import logging

import socket
import time

IS_SAFE = True
NAME = 'mpdStatus'
logger = logging.getLogger('WIDGET')


class mainThread (threading.Thread):
    def __init__(self, codeName, mainQueue, inputQueue=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.codeName = codeName
        self.mainQueue = mainQueue
        self.lastUpdate = "dsadwa"
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        while True:
            status = self.getResultOfCommand("status")
            result = ""
            if 'error' in status:
                result = status['error']
                self.updateContent(self.parse(result))
                time.sleep(10)
                result = ""
            elif status['state'] == "stop":
                result = ""
            elif status['state'] == "pause":
                currentSong = self.getResultOfCommand("currentsong")
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
                currentSong = self.getResultOfCommand("currentsong")
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

            if self.killed():
                break
            self.updateContent(self.parse(result))
            self.idle()
        return 0

    def idle(self):
        "Wait until mpd is on and something has happened"
        while True:
            data = None
            try:
                sock = self.connectTcp('localhost', 6600, timeout=None)
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

    def getResultOfCommand(self, command):
        "Get the result of sending a command to the mpd server"
        data = ""
        try:
            sock = self.connectTcp('localhost', 6600)
            sock.sendall(bytes(command + "\n", encoding="utf-8"))
            while True:
                data += sock.recv(4096).decode("utf-8")
                if data == "" or data.endswith("OK\n"):
                    break
            sock.close()
        except:
            return {'error': 'Connection error'}

        return self.parseInput(data)

    def parseInput(self, data):
        result = {}
        lines = data.splitlines()
        for line in lines:
            if ": " in line:
                key, content = line.split(": ", 1)
                result[key] = content
        return result

    def connectTcp(self, host, port, timeout=2):
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

    def updateContent(self, string):
        if string != self.lastUpdate:
            self.mainQueue.put({
                'name': self.name,
                'codeName': self.codeName,
                'content': string})
            self.lastUpdate = string

    def parse(self, string):
        return string

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()


if __name__ == "__main__":
    import queue

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
        inputQueue=inputQueue)
    thread.start()
    inputThread.start()

    while True:
        print(mainQueue.get()['content'])
