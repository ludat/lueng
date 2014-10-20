import threading
import logging
from Config import CONFIG
CONFIG = CONFIG['OUTPUT_WIDGET']

logger = logging.getLogger('INPUT_WIDGET')


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
                    if hasattr(widget, "inputQueue"):
                        widget.inputQueue.put(string)
                        continue

        for widget in self.Widget.List:
            if widget.inputQueue is not None:
                widget.inputQueue.put("DEATH")

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
