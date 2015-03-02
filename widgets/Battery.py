#!/bin/env python3

import time
import sys
import os


lastUpdate = "dsadwa"

def main():
    powerSupplyPath = ""
    result = ""
    batDir = "/sys/class/power_supply/"
    while True:
        if not os.path.exists(powerSupplyPath):
            power_supplies = os.listdir(batDir)
            for power_supply in power_supplies:
                if "BAT" in power_supply:
                    powerSupplyPath = batDir + power_supply
                    break
            else:
                batteryNotFound()
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

        updateContent(result)
        time.sleep(1)


def batteryNotFound():
    if lastState:
        updateContent("No Bat")
        time.sleep(10)
        updateContent("")
    time.sleep(1)

def updateContent(string):
    global lastUpdate
    if string != lastUpdate:
        printContent(string)
        lastUpdate = string

def printContent(string):
    sys.stdout.write(string+"\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
