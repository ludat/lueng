import threading
import logging
from Config import CONFIG
CONFIG = CONFIG['OUTPUT_WIDGET']

logger = logging.getLogger('OUTPUT_WIDGET')


class WidgetsOutputHandler (threading.Thread):
    "Wait for the output from thread and send response to correct widget"
    def __init__(self, Widget, inputStream):
        threading.Thread.__init__(self)
        self._killed = threading.Event()
        self._killed.clear()
        self.Widget = Widget
        self.name = 'WidgetsOutputHandler'
        self.inputStream = inputStream
        logger.info("Initialized")

    def run(self):
        logger.info("Started")
        while True:
            if self.killed():
                break
            read = self.inputStream.readline()[:-1]
            logger.debug("input: %s", repr(read))
            threadCode, string = read.split("@")
            for widget in self.Widget.List:
                if widget.codeName == threadCode:
                    if widget.p is not None:
                        widget.p.stdin.write(string+"\n")
                        widget.p.stdin.flush()
                        continue

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
