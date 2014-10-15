#!/bin/env python3

import socket
import os

import threading
import logging
from Config import CONFIG
CONFIG = CONFIG['INPUT_WIDGET']

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
        self.createCommandsList()

    def createCommandsList(self):
        """
        I think the best way to implement a command list is a dictionary of
        functions, but I don't want them to be in the class global scope
        and this is an excellent opportunity to use decorators
        """
        @self.decorate
        def start(self, args, opt):
            "start a loaded widget by widget name"
            widget = args[0]
            if self.Widget.start(widget):
                return "Widget started"
            else:
                return "Widget not started because of reasons"

        @self.decorate
        def load(self, args, opt):
            "load a widget without starting it"
            widget = args[0]
            if self.Widget.loadWidget(widget):
                return "Widget loaded"
            else:
                return "Widget not loaded because of reasons"

        @self.decorate
        def reload(self, args, opt):
            "kill and load a widget but without starting it"
            widget = args[0]
            try:
                self.Widget.kill(widget)
                self.Widget.loadWidget(widget)
                return "Widget reloaded"
            except Exception:
                return "Widget not reloaded because of reasons"

        @self.decorate
        def purge(self, args, opt):
            "check if a widget still exists in the fs if not kill it"
            pass

        @self.decorate
        def pause(self, args, opt):
            "pause a widget without killing it (the widget can refuse this)"
            pass

        @self.decorate
        def unpause(self, args, opt):
            "unpause a widget (the widget can refuse this)"
            pass

        @self.decorate
        def ping(self, args, opt):
            "the server will respond pong just to say its alive"
            return "pong\n"

        @self.decorate
        def help(self, args, opt):
            "print the general help or specific to a command (help [cmd])"
            cmd = args[0]
            try:
                return self.commands[cmd].__doc__
            except KeyError:
                logger.warning("command '%s' not found", cmd)
                return ("command '%s' not found".format(cmd))

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
        "This will be very close to the mpd protocol"
        ret = True
        try:
            data = conn.recv(1024).decode('utf-8')
            logger.info("Received: %s", repr(data))
        except:
            logger.warning("recv failed")

        commands = data.splitlines()
        logger.debug("commands: %s", commands)
        response = ""
        for command in commands:
            cmd, args, opt = self.parseInput(command)
            try:
                response += self.commands[cmd](self, args, opt)
            except KeyError:
                response += "command {} not found\n".format(repr(cmd))
                logger.warning("command '%s' not found", repr(cmd))

        try:
            conn.sendall(bytes(response, encoding="utf-8"))
            logger.info("Sent: %s", repr(response))
        except:
            logger.warning("send failed")
        conn.close()
        return ret

    def parseInput(self, input):
        """
        parse the input string
        returns a tupple with
        string: the command issued
        array: with the arguments
        opt: dictionary with pairs option: value
        """
        input = str(input)
        if " " not in input:
            return (input, [], {})
        splitted = input.split(" ")
        return (splitted[0], splitted[1:], {})

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
