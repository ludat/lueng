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
                poll.register(self.eventPipe)
                for widget in self.Widget.List:
                    poll.register(widget.p.stdout)

                p, t = poll.poll()[0]
                codename = None
                for widget in self.Widget.List:
                    if widget.p.stdout.fileno() == p:
                        codename = widget.codeName
                        break
                else:
                    logger.warn("widget id not found")
                    continue

                if t & EPOLLIN:
                    for widget in self.Widget.List:
                        if widget.codeName == codename:
                            data = widget.p.stdout.readline().replace("\n","")
                            widget.updateContent(data)
                            break
                    output = self.Widget.parseToString()
                    logger.debug("Updated output:\n\t%s", output)
                    self.outputStream.write(output)
                    self.outputStream.flush()
                elif t & EPOLLHUP:
                    logger.warn("Got SIGHUP", t)
                else:
                    logger.warn("Some weird code %d", t)

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
