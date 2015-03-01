import threading
import logging
import os
from select import (epoll, EPOLLIN, EPOLLOUT, EPOLLPRI, EPOLLERR, EPOLLHUP,
        EPOLLET, EPOLLONESHOT, EPOLLRDNORM, EPOLLRDBAND, EPOLLWRNORM,
        EPOLLWRBAND, EPOLLMSG)
from Config import CONFIG
CONFIG = CONFIG['INPUT_WIDGET']

logger = logging.getLogger('INPUT_WIDGET')


class WidgetsInputHandler (threading.Thread):
    "Wait for input from queue, parse it and send it to output stream"
    def __init__(self, Widget, widgetEventPipe, outputStream):
        threading.Thread.__init__(self)
        self._killed = threading.Event()
        self._killed.clear()
        self.Widget = Widget
        self.name = 'WidgetsInputHandler'
        self.outputStream = outputStream
        self.eventPipe = widgetEventPipe
        logger.info("Initialized")

    def run(self):
        logger.info("Started")
        while True:
            if self.killed():
                break

            with epoll() as poll:
                logger.debug("Setting up polling")
                poll.register(self.eventPipe)
                for widget in self.Widget.List:
                    poll.register(widget.p.stdout)

                logger.debug("Started polling")
                p, t = poll.poll()[0]
                logger.debug("Got poll")
                codename = None
                for widget in self.Widget.List:
                    if widget.p.stdout.fileno() == p:
                        codename = widget.codeName
                        break
                else:
                    logger.debug("widget id not found")
                    continue

                if t == EPOLLIN:
                    for widget in self.Widget.List:
                        if widget.codeName == codename:
                            widget.updateContent(widget.p.stdout.readline()[:-1])
                            continue
                    output = self.Widget.parseToString()
                    logger.debug("Updated output:\n\t%s", output)
                    self.outputStream.write(output)
                    self.outputStream.flush()
                else:
                    logger.warn("Some weird code %d", t)

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
