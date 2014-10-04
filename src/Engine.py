import queue
import logging
from importlib import import_module, reload
from os.path import isfile
import os

logger = logging.getLogger("Widget")
SAFE_MODULES_ONLY = True


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
        # self.logger.addHandler(consoleLogHandler)

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
        allFiles = os.listdir("widgets.wanted/")
        modulesFiles = [f for f in allFiles if isfile("widgets.wanted/" + f)]
        logger.debug("Modules: " + repr(modulesFiles))
        for fileName in modulesFiles:
            cls.loadModule(fileName)

    @classmethod
    def loadModule(cls, fileName):
        logger.debug("Loading: " + fileName)
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
        except Exception as e:
            logger.warning(str(e))

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
