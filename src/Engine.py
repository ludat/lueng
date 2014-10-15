import queue
import logging
from importlib import import_module, reload
from os.path import isfile
import os
from Config import CONFIG
CONFIG = CONFIG['ENGINE']

logger = logging.getLogger("ENGINE")


class Widget:
    "Instances of this class are widgets and some class methods"
    widgetsList = []
    mainQueue = queue.Queue()
    NEEDED = ("mainThread", "IS_SAFE", "NAME",)
    NEEDED_INSIDE_THREAD = ("name", "kill", "run",)

    def __init__(self, module, fileName):
        "Initialize new from module and add it to the widgetsList"
        for need in self.NEEDED:
            if not hasattr(module, need):
                raise Widget.BadInitializationException(
                    "Missing object in module: " + need)

        self.inputQueue = queue.Queue()

        if CONFIG['SAFE_MODULES_ONLY']:
            if module.IS_SAFE:
                self.thread = module.mainThread(
                    self.mainQueue,
                    inputQueue=self.inputQueue)
            else:
                raise Widget.NotSafeException(
                    "Unsafe thread in safe enviroment")
        else:
            self.thread = module.mainThread(
                self.mainQueue,
                inputQueue=self.inputQueue)

        for need in self.NEEDED_INSIDE_THREAD:
            if not hasattr(self.thread, need):
                raise Widget.BadInitializationException(
                    "Missing object in main thread: " + need)

        self.name = module.NAME
        self.fileName = fileName
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
        for thread in cls.widgetsList:
            if thread.content:
                if string == "":
                    string = thread.content
                else:
                    string = thread.content + separator + string
        return (string+"\n")

    @classmethod
    def startAllWidgets(cls):
        "Start all threads from all instances of Widget class"
        for widget in cls.widgetsList:
            if not widget.thread.is_alive():
                widget.start()

    @classmethod
    def startWidget(cls, widgetName):
        for widget in cls.WidgetsList:
            if widget.name == widgetName:
                widget.start()
                return True
        else:
            return False

    @classmethod
    def killAllWidgets(cls):
        "Kill all threads from all instances of Widget class"
        for widget in cls.widgetsList:
            widget.kill()

    @classmethod
    def killWidget(cls, widgetName):
        for widget in cls.WidgetsList:
            if widget.name == widgetName:
                widget.kill()
                return True
        else:
            return False

    @classmethod
    def loadAllWidgets(cls):
        modules = []
        allFiles = os.listdir("widgets.wanted/")
        modulesFiles = [
            f[:-3] for f in allFiles if isfile("widgets.wanted/" + f)]
        logger.debug("Modules: " + repr(modulesFiles))
        for fileName in modulesFiles:
            modules.append(
                cls._loadModuleByFileName(fileName))

        for module, fileName in modules:
            if module is None:
                return False
            try:
                widget = cls(module, fileName)
                cls._addToList(widget)
            except Exception as e:
                logger.error(repr(e))

    @classmethod
    def loadWidget(cls, WidgetName):
        module, fileName = cls._loadModuleByWidgetName(WidgetName)
        if module is None:
            return False
        try:
            widget = cls(module, fileName)
        except Exception as e:
            logger.error(repr(e))
            return False
        return cls._addToList(widget)

    @classmethod
    def unloadModule(cls, fileName):
        "Kill a thread and remove it from widgetsList"
        for i in range(len(cls.widgetsList)):
            if cls.widgetsList[i].fileName == fileName:
                cls.widgetsList[i].kill()
                del cls.widgetsList[i]
                break

    @classmethod
    def pauseWidget(cls, widgetName):
        for widget in cls.WidgetsList:
            if widget.name == widgetName:
                widget.pause()
                return True
        else:
            return False

    @classmethod
    def unpauseWidget(cls, widgetName):
        for widget in cls.WidgetsList:
            if widget.name == widgetName:
                widget.unpause()
                return True
        else:
            return False

    @classmethod
    def _addToList(cls, widget):
        if widget.fileName in [w.fileName for w in cls.widgetsList]:
            logger.info("Colliding fileName, not loading")
            return

        if widget.name in [w.name for w in cls.widgetsList]:
            logger.info("Colliding name, not loading")
            return

        for i in range(len(cls.widgetsList)):
            if cls.widgetsList[i].fileName > widget.fileName:
                cls.widgetsList.insert(i, widget)
                break
        else:
            cls.widgetsList.append(widget)

    @classmethod
    def _loadModuleByWidgetName(cls, widgetName):
        "This shit should load widgets by widget name"
        modulesList = []
        allFiles = os.listdir("widgets.wanted/")
        modulesFiles = [
            f[:-3] for f in allFiles if isfile("widgets.wanted/" + f)]
        logger.debug("Modules: " + repr(modulesFiles))
        for fileName in modulesFiles:
            modulesList.append(
                cls._loadWidgetByFileName(fileName))
        for module, fileName in modulesList:
            if hasattr(module, 'NAME'):
                if module.NAME == widgetName:
                    return (module, fileName)
        else:
            return (None, "")

    @classmethod
    def _loadModuleByFileName(cls, fileName):
        "This shit should load widgets by file name"
        try:
            module = reload(import_module(fileName))
        except ImportError as e:
            logger.info(
                "{}: NOT Loaded Reason: {}".format(fileName, repr(e)))
            return (None, "")
        except Exception as e:
            logger.critical(str(e))
            return (None, "")
        return (module, fileName)

    @classmethod
    def reloadModule(cls, fileName):
        cls.unloadModule(fileName)
        cls.loadModule(fileName)

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
