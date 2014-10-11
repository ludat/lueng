#!/bin/env python3

import threading
import logging

import time
import os

IS_SAFE = True
NAME = 'battery'
logger = logging.getLogger('WIDGET')


class mainThread (threading.Thread):
    def __init__(self, mainQueue, inputQueue=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.mainQueue = mainQueue
        self.lastUpdate = "dsadwa"
        self._killed = threading.Event()
        self._killed.clear()
        self.lastState = True

    def run(self):
        powerSupplyPath = ""
        result = ""
        batDir = "/sys/class/power_supply/"
        while True:
            if not os.path.exists(powerSupplyPath):
                power_supplies = os.listdir(batDir)
                for power_supply in power_supplies:
                    if "BAT" in power_supply:
                        powerSupplyPath = batDir + power_supply
                        self.lastState = True
                        break
                else:
                    self.batteryNotFound()
                    continue

            statusFile = open(powerSupplyPath + "/status")
            chargeFullFile = open(powerSupplyPath + "/charge_full")
            chargeNowFile = open(powerSupplyPath + "/charge_now")

            status = statusFile.read()[:-1]
            chargeFull = int(chargeFullFile.read())
            chargeNow = int(chargeNowFile.read())

            statusFile.close()
            chargeFullFile.close()
            chargeNowFile.close()

            if status == "":
                result = ""
            elif status == "Unknown":
                result = ""
            elif status == "Full":
                result = ""
            elif status == "Charging":
                result = (
                    "^i(icons/xbm/bat_full_02.xbm) "
                    "{}%".format(round(chargeNow*100/chargeFull))
                )
            elif status == "Discharging":
                result = (
                    "^i(icons/xbm/bat_empty_02.xbm) "
                    "{}%".format(round(chargeNow*100/chargeFull))
                )
            else:
                result = "Unmanaged battery status: " + status

            if self.killed():
                break
            self.updateContent(result)
            time.sleep(1)

    def updateContent(self, string):
        if string != self.lastUpdate:
            self.mainQueue.put({'name': self.name, 'content': string})
            self.lastUpdate = string

    def batteryNotFound(self):
        if self.lastState:
            self.updateContent("No Bat")
            time.sleep(10)
            self.updateContent("")
        self.lastState = False
        time.sleep(1)

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    import queue

    class TestInputThread(threading.Thread):
        def __init__(self, inputQueue):
            threading.Thread.__init__(self)
            self.inputQueue = inputQueue

        def run(self):
            while True:
                self.inputQueue.put(input())

    inputQueue = queue.Queue()
    mainQueue = queue.Queue()

    inputThread = TestInputThread(inputQueue)

    thread = mainThread(
        mainQueue,
        inputQueue=inputQueue)
    thread.start()
    inputThread.start()

    while True:
        print(mainQueue.get()['content'])
