#!/bin/env python3

import socket
import os

import threading
import logging
from Config import CONFIG
CONFIG = CONFIG['INPUT_SERVER']

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
            widgetCode = args[0]
            if self.Widget.startWidget(widgetCode):
                return "Widget started"
            else:
                return "Widget not started because of reasons"

        @self.decorate
        def load(self, args, opt):
            "load a widget without starting it"
            fileName = args[0]
            try:
                self.Widget.loadWidget(fileName)
                return "Widget loaded\n"
            except Exception as e:
                logger.warning(str(e))
                return str(e)

        @self.decorate
        def unload(self, args, opt):
            "kill and unload a widget by its code"
            codeName = args[0]
            try:
                self.Widget.unloadWidget(codeName)
                return "Widget unloaded\n"
            except Exception as e:
                logger.warning(str(e))
                return str(e)

        @self.decorate
        def pause(self, args, opt):
            "pause a widget without killing it (the widget can refuse this)"
            return "Not implemented yet"

        @self.decorate
        def unpause(self, args, opt):
            "unpause a widget (the widget can refuse this)"
            return "Not implemented yet"

        @self.decorate
        def ls(self, args, opt):
            "List loaded widgets"
            ret = ""
            for file in self.Widget.getAvailableModules():
                ret += "{}\n".format(
                    file
                )
            return ret

        @self.decorate
        def list(self, args, opt):
            "List loaded widgets"
            ret = ""
            for widget in self.Widget.List:
                ret += "{:3} - {:40}{}\n".format(
                    widget.codeName,
                    widget.name,
                    'alive' if widget.thread.is_alive() else 'dead'
                )
            return ret

        @self.decorate
        def ping(self, args, opt):
            "the server will respond pong just to say it's alive"
            return "pong\n"

        @self.decorate
        def help(self, args, opt):
            "print the general help or specific to a command (help [cmd])"
            ret = ""
            cmds = []
            if len(args) == 0:
                cmds = self.commands
            else:
                cmds = args

            for cmd in cmds:
                try:
                    ret += "{:10}{}\n".format(
                        cmd,
                        self.commands[cmd].__doc__
                    )
                except KeyError:
                    logger.warning("command '%s' not found", cmd)
                    ret += "command '{}' not found\n".format(cmd)
            return ret

    def decorate(self, func):
        self.commands[func.__name__] = func
        return func

    def run(self):
        if os.path.exists("/tmp/lueng.sock"):
            logger.warning("Socket file already exists, deleting it")
            os.remove("/tmp/lueng.sock")

        logger.info("Opening socket...")
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind("/tmp/lueng.sock")
        server.listen(5)
        logger.info("Listening... ")

        while True:
            conn, address = server.accept()
            if not self.handle(conn, address):
                break
        logger.info("Shutting down...")
        server.close()
        os.remove("/tmp/lueng.sock")

    def handle(self, conn, address):
        "This will be very close to the mpd protocol"
        ret = True
        try:
            data = conn.recv(1024).decode('utf-8')
            logger.info("Received: %s", repr(data))
        except:
            logger.warning("recv failed")

        commands = data.splitlines()
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
        cmd = ""
        args = []
        opt = {}
        splitted = input.split(" ", 1)
        if len(splitted) == 1:
            cmd = splitted[0]
        else:
            cmd = splitted[0]
            args = splitted[1].split(" ")
            for i in range(len(args)):
                if args[i] == "":
                    del args[i]

        return (cmd, args, opt)

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
