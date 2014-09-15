#!/bin/env python3

import threading
import time

import os

IS_SAFE = True
NAME = 'battery'


class mainThread (threading.Thread):
    def __init__(self, mainQueue, inputQueue=None, logger=None):
        threading.Thread.__init__(self)
        self.name = NAME
        self.logger = logger
        self.mainQueue = mainQueue
        self._killed = threading.Event()
        self._killed.clear()

    def run(self):
        powerSupplyPath = None
        power_supplies = os.listdir("/sys/class/power_supply")
        for power_supply in power_supplies:
            if "BAT" in power_supply:
                powerSupplyPath = "/sys/class/power_supply/" + power_supply
                break
        else:
            self.batteryNotFound()
            return

        result = ""
        while True:
            statusFile = open(powerSupplyPath + "/status")
            chargeFullFile = open(powerSupplyPath + "/charge_full")
            chargeNowFile = open(powerSupplyPath + "/charge_now")

            status = statusFile.read()[:-1]
            chargeFull = int(chargeFullFile.read())
            chargeNow = int(chargeNowFile.read())

            if status == "":
                result = ""
            elif status == "Unknown":
                result = ""
            elif status == "Full":
                result = ""
            elif status == "Charging":
                result = str(round(chargeNow*100/chargeFull)) + "%"
            elif status == "Discharging":
                result = str(round(chargeNow*100/chargeFull)) + "%"
            else:
                result = "Unmanaged battery status:" + status
            if self.killed():
                break
            self.mainQueue.put({'name': self.name, 'content': result})
            time.sleep(3)

    def batteryNotFound(self):
        pass

    def killed(self):
        return self._killed.is_set()

    def kill(self):
        self._killed.set()

if __name__ == "__main__":
    pass
