import queue
import logging
from importlib import import_module, reload
from random import shuffle
from os.path import isfile
import os
from Config import CONFIG
CONFIG = CONFIG['ENGINE']

logger = logging.getLogger("ENGINE")


class Widget:
    "Instances of this class are widgets and some class methods"
    List = []
    mainQueue = queue.Queue()
    NEEDED = ("mainThread", "IS_SAFE", "NAME",)
    NEEDED_INSIDE_THREAD = ("name", "kill", "run",)

    def __init__(self, module, codeName):
        "Initialize new from module and add it to the List"
        for need in self.NEEDED:
            if not hasattr(module, need):
                raise Widget.BadInitializationException(
                    "Missing object in module: " + need)

        self.inputQueue = queue.Queue()

        self.codeName = codeName

        if CONFIG['SAFE_MODULES_ONLY']:
            if module.IS_SAFE:
                self.thread = module.mainThread(
                    self.codeName,
                    self.mainQueue,
                    inputQueue=self.inputQueue)
            else:
                raise Widget.NotSafeException(
                    "Unsafe thread in safe enviroment")
        else:
            self.thread = module.mainThread(
                self.codeName,
                self.mainQueue,
                inputQueue=self.inputQueue)

        for need in self.NEEDED_INSIDE_THREAD:
            if not hasattr(self.thread, need):
                raise Widget.BadInitializationException(
                    "Missing object in main thread: " + need)

        self.name = module.NAME
        self.fileName = module.__file__
        self.content = "Nothing yet"

    def updateContent(self, newContent):
        "Update the actual content with some new content sent by the thread"
        self.content = newContent

    def pause(self):
        "pause this thread"
        self.thread.pause()
        logger.info("Thread '" + self.name + "' paused")

    def unpause(self):
        "unpause this thread"
        self.thread.unpause()
        logger.info("Thread '" + self.name + "' unpaused")

    def kill(self):
        "Kill this thread"
        self.thread.kill()
        logger.info("Thread '" + self.name + "' killed")

    def start(self):
        "Start this thread"
        self.thread.start()
        logger.info("Thread '" + self.name + "' started")

    @classmethod
    def parseToString(cls, separator=" < "):
        "Parse the skeleton into a string to pass it to dzen "
        string = ""
        for thread in cls.List:
            if thread.content:
                if string == "":
                    string = thread.content
                else:
                    string = thread.content + separator + string
        return (string+"\n")

    @classmethod
    def getNewId(cls):
        chars = list(map(chr, range(97, 123)))
        shuffle(chars)
        chars1 = chars.copy()
        shuffle(chars)
        chars2 = chars.copy()
        shuffle(chars)
        chars3 = chars.copy()
        for char1 in chars1:
            for char2 in chars2:
                for char3 in chars3:
                    code = char1 + char2 + char3
                    if code not in [w.codeName for w in cls.List]:
                        return code
        else:
            raise Exception("Couldn't find an appropiate code")

    @classmethod
    def getAvailableModules(cls):
        files = os.listdir("widgets.wanted/")
        return [
            f[:-3] for f in files if isfile("widgets.wanted/" + f)]

    @classmethod
    def startAllWidgets(cls):
        "Start all threads from all instances of Widget class"
        for widget in cls.List:
            if not widget.thread.is_alive():
                widget.start()

    @classmethod
    def startWidget(cls, codeName):
        for widget in cls.List:
            if widget.codeName == codeName:
                widget.start()
                return True
        else:
            return False

    @classmethod
    def killAllWidgets(cls):
        "Kill all threads from all instances of Widget class"
        for widget in cls.List:
            widget.kill()

    @classmethod
    def killWidget(cls, codeName):
        for widget in cls.List:
            if widget.codeName == codeName:
                widget.kill()
                return True
        else:
            return False

    @classmethod
    def unloadWidget(cls, codeName):
        "Kill a thread and remove it from List"
        for i in range(len(cls.List)):
            if cls.List[i].codeName == codeName:
                cls.List[i].kill()
                del cls.List[i]
                break

    @classmethod
    def pauseWidget(cls, codeName):
        for widget in cls.List:
            if widget.codeName == codeName:
                widget.pause()
                return True
        else:
            return False

    @classmethod
    def unpauseWidget(cls, codeName):
        for widget in cls.List:
            if widget.codeName == codeName:
                widget.unpause()
                return True
        else:
            return False

    @classmethod
    def _loadModuleByFileName(cls, fileName):
        "This shit should load widgets by file name"
        try:
            module = reload(import_module(fileName))
        except ImportError as e:
            logger.info(
                "{}: NOT Loaded Reason: {}".format(fileName, repr(e)))
            raise e
        except Exception as e:
            logger.critical(str(e))
            raise e
        return module

    @classmethod
    def loadAllWidgets(cls):
        modulesFiles = cls.getAvailableModules()
        logger.debug("Modules: " + repr(modulesFiles))
        for fileName in modulesFiles:
            cls.loadWidget(fileName)

    @classmethod
    def loadWidget(cls, fileName):
        module = cls._loadModuleByFileName(fileName)
        widget = cls(module, cls.getNewId())
        cls._addToList(widget)

    @classmethod
    def _addToList(cls, widget):
        if widget.codeName in [w.codeName for w in cls.List]:
            logger.info("Colliding code name, not loading")
            return

        for i in range(len(cls.List)):
            if cls.List[i].fileName > widget.fileName:
                cls.List.insert(i, widget)
                break
        else:
            cls.List.append(widget)

    @staticmethod
    class NotSafeException (Exception):
        "Not-safe thread in a safe enviroment"
        pass

    @staticmethod
    class BadInitializationException (Exception):
        "Module not correctly initialz¡ized"
        pass
