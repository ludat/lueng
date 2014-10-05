import threading
from Config import CONFIG
CONFIG = CONFIG['INPUT_WIDGET']


class WidgetsInputHandler (threading.Thread):
    "Wait for input from queue, parse it and send it to output stream"
    def __init__(self, Widget, outputStream):
        threading.Thread.__init__(self)
        self._killed = threading.Event()
        self._killed.clear()
        self.Widget = Widget
        self.name = 'WidgetsInputHandler'
        self.outputStream = outputStream

    def run(self):
        while True:
            if self.killed():
                break
            item = self.Widget.mainQueue.get()
            for widget in self.Widget.widgetsList:
                if widget.name == item['name']:
                    widget.updateContent(item['content'])
                    continue

            self.outputStream.write(self.Widget.parseToString())
            self.outputStream.flush()

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()
