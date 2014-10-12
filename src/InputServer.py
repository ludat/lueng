#!/bin/env python3

import socket
import os

import threading
import logging
# from Config import CONFIG
# CONFIG = CONFIG['INPUT_WIDGET']

logger = logging.getLogger('INPUT_SERVER')


class InputServer(threading.Thread):
    "Unix socket server for interaction with the user"
    def __init__(self, Widget):
        threading.Thread.__init__(self)
        self._killed = threading.Event()
        self._killed.clear()
        self.Widget = Widget
        self.name = 'SocketInputServer'
        self.commands = {}

        # I think the best way to implement a command list is a dictionary of
        # functions, but I don't want them to be in the class global scope
        # and this is an excellent opportunity to use decorators
        @self.decorate
        def kill(self):
            logger.warning("I should be dead :D")
            return "Someone somewhere died\n"

        @self.decorate
        def ping(self):
            return "pong\n"

        @self.decorate
        def list(self):
            resp = ""
            for widget in self.Widget.widgetsList:
                resp += "{}:{}:{}\n".format(
                    widget.name,
                    widget.fileName,
                    widget.thread.is_alive())
            return resp

        @self.decorate
        def reload(self):
            return "Not implemented yet\n"

        @self.decorate
        def load(self):
            return "Not implemented yet\n"

        @self.decorate
        def disable(self):
            return "Not implemented yet\n"

        @self.decorate
        def enable(self):
            return "Not implemented yet\n"

    def decorate(self, func):
        self.commands[func.__name__] = func
        return func

    def run(self):
        if os.path.exists("/tmp/SB"):
            logger.warning("Socket file already exists, deleting it")
            os.remove("/tmp/SB")

        logger.info("Opening socket...")
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind("/tmp/SB")
        server.listen(5)
        logger.info("Listening... ")

        while True:
            conn, address = server.accept()
            if not self.handle(conn, address):
                break
        logger.info("Shutting down...")
        server.close()
        os.remove("/tmp/SB")

    def handle(self, conn, address):
        # This will be very close to the mpd protocol
        ret = True
        try:
            data = conn.recv(1024).decode('utf-8')
            logger.info("Received: %s", repr(data))
        except:
            logger.warning("recv failed")

        commands = data.splitlines()
        response = ""
        for command in commands:
            c = command.split(" ", 1)
            try:
                response += self.commands[c[0]](self)
            except KeyError:
                response += "command '%s' not found\n".format(c[0])
                logger.warning("command '%s' not found", c[0])

        try:
            conn.sendall(bytes(response, encoding="utf-8"))
            logger.info("Sent: %s", repr(response))
        except:
            logger.warning("send failed")
        conn.close()
        return ret

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
