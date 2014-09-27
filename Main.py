#!/bin/env python3

import threading
import queue
import subprocess
import time
import logging

import os
from os.path import isfile, exists
import sys

from importlib import import_module, reload

SAFE_MODULES_ONLY = True
USE_INOTIFY = True
os.chdir(os.path.dirname(__file__) + "/widgets/")
sys.path.append(os.getcwd())

paths = os.getenv("PATH").split(":")
for path in paths:
    if exists(path+"/inotifywait"):
        break
else:
    USE_INOTIFY = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(levelname)s:%(name)s:%(message)s')

# # Add FileHandler
# now = datetime.datetime.now()
# timeStamp = now.strftime("%Y-%m-%d_%H:%M:%S")
# del datetime  # fuck you datetime
#
# fileLogHandler = logging.FileHandler("{}.statusBar.log".format(timeStamp))
# fileLogHandler.name = 'File Logger'
# fileLogHandler.level = logging.DEBUG
# fileLogHandler.formatter = formatter
# logger.addHandler(fileLogHandler)

# Add ConsoleHandler
consoleLogHandler = logging.StreamHandler()
consoleLogHandler.name = 'Console Logger'
consoleLogHandler.level = logging.DEBUG
consoleLogHandler.formatter = formatter
logger.addHandler(consoleLogHandler)


class WidgetsOutputHandler (threading.Thread):
    "Wait for the output from thread and send response to correct widget"
    def __init__(self, Widget, inputStream):
        threading.Thread.__init__(self)
        self._killed = threading.Event()
        self._killed.clear()
        self.name = 'WidgetsOutputHandler'
        self.inputStream = inputStream

    def run(self):
        while True:
            if self.killed():
                break
            read = self.inputStream.readline()[:-1]
            logger.debug("input:'" + read + "'")
            threadName, string = read.split("@")
            for widget in Widget.widgetsList:
                if widget.name == threadName:
                    if hasattr(widget, "inputQueue"):
                        widget.inputQueue.put(string)
                        continue

        for widget in Widget.widgetsList:
            if widget.inputQueue is not None:
                widget.inputQueue.put("DEATH")

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()


class WidgetsInputHandler (threading.Thread):
    "Wait for input from queue, parse it and send it to output stream"
    def __init__(self, Widget, outputStream):
        threading.Thread.__init__(self)
        self._killed = threading.Event()
        self._killed.clear()
        self.name = 'WidgetsInputHandler'
        self.outputStream = outputStream

    def run(self):
        while True:
            if self.killed():
                break
            item = Widget.mainQueue.get()
            for widget in Widget.widgetsList:
                if widget.name == item['name']:
                    widget.updateContent(item['content'])
                    continue

            self.outputStream.write(Widget.parseToString())
            self.outputStream.flush()

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()


class WidgetsReloader (threading.Thread):
    "Monitor widget file and reload them if needed"
    def __init__(self, Widget):
        threading.Thread.__init__(self)
        self._killed = threading.Event()
        self._killed.clear()
        self.name = 'WidgetsReloades'

    def run(self):
        inoProc = subprocess.Popen(
            ["inotifywait",
                "--event", "modify,create,move,delete",
                "-m", "."],
            stdout=subprocess.PIPE,
            cwd="../",
            universal_newlines=True)

        while True:
            if self.killed():
                break
            read = inoProc.stdout.readline()
            folder, event, fileName = read[:-1].split(" ", 2)
            if (folder != "./" or
                    fileName[-3:] != ".py"):
                continue

            if event == "DELETE":
                Widget.unloadModule(fileName)
            elif event == "MOVED_FROM":
                Widget.unloadModule(fileName)
            elif event == "MOVED_TO":
                Widget.loadModule(fileName)
            elif event == "CREATE":
                Widget.loadModule(fileName)
            elif event == "MODIFY":
                Widget.reloadModule(fileName)

            Widget.startAll()

        inoProc.kill()

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()


class Widget:
    "Instances of this class are widgets and some class method "
    widgetsList = []
    mainQueue = queue.Queue()
    NEEDED = ("mainThread", "IS_SAFE", "NAME",)
    NEEDED_INSIDE_THREAD = ("name", "kill", "run",)

    def __init__(self, module, fileName):
        "Initialize new from module and add it to the widgetsList"
        for obj in self.NEEDED:
            if not hasattr(module, obj):
                raise Widget.BadInitializationException(
                    "Missing object in module: "+obj)

        self.inputQueue = queue.Queue()

        self.logger = logging.getLogger("Widget." + module.NAME)
        # self.logger.addHandler(fileLogHandler)
        self.logger.addHandler(consoleLogHandler)

        if SAFE_MODULES_ONLY:
            if module.IS_SAFE:
                self.thread = module.mainThread(
                    self.mainQueue,
                    inputQueue=self.inputQueue,
                    logger=self.logger)
            else:
                raise Widget.NotSafeException(
                    "Unsafe thread in safe enviroment")
        else:
            self.thread = module.mainThread(
                self.mainQueue,
                inputQueue=self.inputQueue,
                logger=self.logger)

        for obj in self.NEEDED_INSIDE_THREAD:
            if not hasattr(self.thread, obj):
                raise Widget.BadInitializationException(
                    "Missing object in main thread: "+obj)

        self.name = self.thread.name
        self.fileName = fileName
        for widget in self.widgetsList:
            if self.name == widget.name or self.fileName == widget.fileName:
                raise Widget.CollidingNamesException()
        self.content = "Nothing yet"

    def updateContent(self, newContent):
        "Update the actual content with some new content sent by the thread"
        self.content = newContent

    def kill(self):
        "Kill this thread"
        self.thread.kill()
        logger.info("Thread '" + self.name + "' killed")

    def start(self):
        "Start this thread"
        self.thread.start()
        logger.info("Thread '" + self.name + "' started")

    @classmethod
    def startAll(cls):
        "Start all threads from all instances of Widget class"
        for thread in cls.widgetsList:
            if not thread.thread.is_alive():
                thread.start()

    @classmethod
    def killAll(cls):
        "Kill all threads from all instances of Widget class"
        for thread in cls.widgetsList:
            thread.kill()

    @classmethod
    def parseToString(cls, separator=" < "):
        "Parse the skeleton into a string to pass it to dzen "
        string = ""
        for thread in cls.widgetsList:
            if thread.content:
                if string == "":
                    string = thread.content
                else:
                    string = thread.content + separator + string
        return (string+"\n")

    @classmethod
    def loadAllModules(cls):
        allFiles = os.listdir("./")
        modulesFiles = [f for f in allFiles if isfile(f)]
        for fileName in modulesFiles:
            cls.loadModule(fileName)

    @classmethod
    def loadModule(cls, fileName):
        try:
            module = reload(import_module(fileName[:-3]))
            for i in range(len(cls.widgetsList)):
                if cls.widgetsList[i].fileName > fileName:
                    cls.widgetsList.insert(i, cls(module, fileName))
                    break
            else:
                cls.widgetsList.append(cls(module, fileName))
        except (ImportError,
                Widget.CollidingNamesException,
                Widget.BadInitializationException,
                Widget.NotSafeException) as e:
            logger.info(
                "{}: NOT Loaded Reason: {}".format(fileName, str(e)))

    @classmethod
    def unloadModule(cls, fileName):
        "Kill a thread and remove it from widgetsList"
        for i in range(len(cls.widgetsList)):
            if cls.widgetsList[i].fileName == fileName:
                cls.widgetsList[i].kill()
                del cls.widgetsList[i]
                break

    @classmethod
    def reloadModule(cls, fileName):
        cls.unloadModule(fileName)
        cls.loadModule(fileName)

    @classmethod
    def debug(cls, word):
        logger.debug(word + ":" + str([f.fileName for f in cls.widgetsList]))

    @staticmethod
    class NotSafeException (Exception):
        "Not-safe thread in a safe enviroment"
        pass

    @staticmethod
    class BadInitializationException (Exception):
        "Module not correctly initialz¡ized"
        pass

    @staticmethod
    class CollidingNamesException (Exception):
        "Can't have two modules with the same name"
        pass


def main():
    widgetsMonitor = WidgetsReloader(Widget)

    Widget.loadAllModules()

    Widget.startAll()

    if USE_INOTIFY:
        widgetsMonitor.start()

    dzenProcess = subprocess.Popen(
        ["dzen2",
            "-ta", "r",
            "-bg", "#161616",
            "-fn", "Terminus:size=8",
            "-w", "1300",
            "-x", "500",
            "-e", "",
            "-dock"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True)

    widgetsInputHandler = WidgetsInputHandler(Widget, dzenProcess.stdin)

    widgetsOutputHandler = WidgetsOutputHandler(Widget, dzenProcess.stdout)

    widgetsInputHandler.start()

    widgetsOutputHandler.start()

    while True:
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Exiting...")
            widgetsMonitor.kill()
            widgetsInputHandler.kill()
            widgetsOutputHandler.kill()
            dzenProcess.terminate()
            Widget.killAll()
            return 0


if __name__ == "__main__":
    logger.debug("Program started")
    logger.debug(os.getcwd())
    main()
    logger.warning("Main thread is dead!")
