import threading
from Config import CONFIG
CONFIG = CONFIG['OUTPUT_WIDGET']


class WidgetsOutputHandler (threading.Thread):
    "Wait for the output from thread and send response to correct widget"
    def __init__(self, Widget, inputStream):
        threading.Thread.__init__(self)
        self._killed = threading.Event()
        self._killed.clear()
        self.Widget = Widget
        self.name = 'WidgetsOutputHandler'
        self.inputStream = inputStream

    def run(self):
        while True:
            if self.killed():
                break
            read = self.inputStream.readline()[:-1]
            # logger.debug("input:'" + read + "'")
            threadName, string = read.split("@")
            for widget in self.Widget.widgetsList:
                if widget.name == threadName:
                    if hasattr(widget, "inputQueue"):
                        widget.inputQueue.put(string)
                        continue

        for widget in self.Widget.widgetsList:
            if widget.inputQueue is not None:
                widget.inputQueue.put("DEATH")

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
