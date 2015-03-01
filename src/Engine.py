import queue
import logging
from random import shuffle
from os.path import isfile, islink, basename, realpath, exists
import os
from Config import CONFIG
CONFIG = CONFIG['ENGINE']

logger = logging.getLogger("ENGINE")


class Widget:
    "Instances of this class are widgets and some class methods"
    List = []
    SubscribersPipes = []
    WANTED = ("name", "is_safe",)

    def __init__(self, filePath, codeName):
        "Initialize new from module and add it to the List"
        #TODO check if stuff is valid and raise exceptions if not
        self.codeName = codeName
        self.filePath = filePath
        self.fileName = basename(filePath)
        self.name = basename(realpath(filePath))
        self.PID = 0
        self.content = "Nothing yet"

    def updateContent(self, newContent):
        "Update the actual content with some new content sent by the process"
        self.content = newContent

    def pause(self):
        "pause this process"
        #TODO Will SIGSTOP do the job here?
        logger.info("process '" + self.name + "' paused")

    def unpause(self):
        "unpause this process"
        #TODO Will SIGCONT do the job here?
        logger.info("process '" + self.name + "' unpaused")

    def kill(self):
        "Kill this process"
        #TODO I guess SIGINT will do the job
        logger.info("process '" + self.name + "' killed")

    def start(self):
        "Start this process"
        #TODO start the process with popen
        logger.info("process '" + self.name + "' started")

    @classmethod
    def parseToString(cls, separator=" < "):
        "Parse the skeleton into a string to pass it to dzen "
        string = ""
        for process in cls.List:
            if process.content:
                if string == "":
                    string = process.content
                else:
                    string = process.content + separator + string
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
    def getNewSubscriberPipe(cls):
        "Create a read/write pipe pair to publish changes to widget class"
        r, w = os.pipe()
        cls.SubscribersPipes.append(open(w, mode='w'))
        return open(r, mode='r')

    @classmethod
    def getAvailableModules(cls):
        files = os.listdir("widgets.wanted/")
        return [
            f for f in files if isfile("widgets.wanted/" + f)]

    @classmethod
    def startAllWidgets(cls):
        "Start all threads from all instances of Widget class"
        for widget in cls.List:
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
    def loadAllWidgets(cls):
        files = cls.getAvailableModules()
        logger.debug("Modules: " + repr(files))
        for fileName in files:
            cls.loadWidget(fileName)

    @classmethod
    def loadWidget(cls, fileName):
        widget = cls(fileName, cls.getNewId())
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
