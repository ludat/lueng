#!/bin/env python3

import threading

import re
import socket

IS_SAFE = True
NAME = 'mpdStatus'


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
        statusRegex = re.compile(
            (
                "volume: (?P<volume>[0-9\\-]+).*?"
                "repeat: (?P<repeat>[0-9]+).*?"
                "random: (?P<random>[0-9]+).*?"
                "single: (?P<single>[0-9]+).*?"
                "consume: (?P<consume>[0-9]+).*?"
                "playlist: (?P<playlist>[0-9]+).*?"
                "playlistlength: (?P<playlistlenght>[0-9]+).*?"
                "mixrampdb: (?P<mixrampdb>[0-9\\.]+).*?"
                "state: (?P<state>\w+).*?"
                "song: (?P<song>[0-9]+).*?"
                "songid: (?P<songid>[0-9]+).*?"
                # "time: (?P<time>[0-9:]+).*?"
                # "elapsed: (?P<elapsed>[0-9\\.]+).*?"
                # "bitrate: (?P<bitrate>[0-9]+).*?"
                # "audio: (?P<audio>[0-9a-z:]+).*?"
                "nextsong: (?P<nextsong>[0-9]+).*?"
                "nextsongid: (?P<nextsongid>[0-9]+).*?"
            ),
            re.DOTALL)
        currentSongRegex = re.compile(
            (
                "file: (?P<file>[^\n]+).*?"
                "Last-Modified: (?P<last_modified>[^\n]+).*?"
                "Time: (?P<time>[^\n]+).*?"
                "Artist: (?P<artist>[^\n]+).*?"
                "Album: (?P<album>[^\n]+).*?"
                "Title: (?P<title>[^\n]+).*?"
                "Date: (?P<date>[^\n]+).*?"
                "Disc: (?P<disc>[^\n]+).*?"
                "AlbumArtist: (?P<albumartist>[^\n]+).*?"
                "Pos: (?P<pos>[^\n]+).*?"
                "Id: (?P<id>[^\n]+).*?"
            ),
            re.DOTALL)

        while True:
            statusRaw = self.getResultOfCommand("status")
            status = statusRegex.search(statusRaw).groupdict()
            result = ""
            # TODO replace this strings with icons
            if status['state'] == "stop":
                result = ""
            elif status['state'] == "pause":
                result = "paused {}% - ".format(status['volume'])
                currentSongRaw = self.getResultOfCommand("currentsong")
                currentSong = currentSongRegex.search(currentSongRaw).groupdict()
                result += "{} - {}".format(
                    currentSong['title'], currentSong['artist'])
            elif status['state'] == "play":
                result = "playing {}% - ".format(status['volume'])
                currentSongRaw = self.getResultOfCommand("currentsong")
                currentSong = currentSongRegex.search(currentSongRaw).groupdict()
                result += "{} - {}".format(
                    currentSong['title'], currentSong['artist'])
            else:
                result = "SHIT"

            if self.killed():
                break
            self.updateContent(self.parse(result))
            self.getResultOfCommand("idle")
        self.sock.close()
        self.inputThread.kill()
        return 0

    def updateContent(self, string):
        if string != self.lastUpdate:
            self.mainQueue.put({'name': self.name, 'content': string})
            self.lastUpdate = string

    def getResultOfCommand(self, command):
        sock = None
        if command == "idle":
            sock = self.connectTcp('localhost', 6600, timeout=None)
        else:
            sock = self.connectTcp('localhost', 6600)

        sock.sendall(bytes(command + "\n", encoding="utf-8"))
        data = ""
        while True:
            data = sock.recv(4096).decode("utf-8")
            if data == "" or data.endswith("OK\n"):
                break
        sock.close()
        return data

    def connectTcp(self, host, port, timeout=2):
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

    def parse(self, string):
        return string

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
