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

    def run(self):
        if os.path.exists("/tmp/SB"):
            logger.warning("Socket file already exists, deleting it")
            os.remove("/tmp/SB")

        logger.info("Opening socket...")
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind("/tmp/SB")
        server.listen(5)
        logger.info("Listening...")

        while True:
            conn, address = server.accept()
            if not self.handle(conn, address):
                break
        logger.info("Shutting down...")
        server.close()
        os.remove("/tmp/SB")

    def handle(self, conn, address):
        ret = True
        try:
            data = conn.recv(1024).decode('utf-8')
            logger.info("Recived: %s", repr(data))
        except:
            logger.warning("recv failed")
            ret = True
        if data == "kill":
            ret = False

        try:
            conn.sendall(bytes(data, encoding="utf-8"))
            logger.info("Sent: %s", repr(data))
        except:
            logger.warning("send failed")
            ret = True
        conn.close()
        return ret

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
