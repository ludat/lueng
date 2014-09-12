#! /bin/env python3
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject

bus = dbus.SystemBus()

eth0 = bus.get_object('org.freedesktop.NetworkManager',
                      '/org/freedesktop/NetworkManager/AccessPoint/144')

eth0_dev_iface = dbus.Interface(eth0,
    # dbus_interface='org.freedesktop.NetworkManager.AccessPoint')
    dbus_interface='org.freedesktop.DBus.Properties')
props = eth0_dev_iface.Get("org.freedesktop.NetworkManager.AccessPoint","Strength")
# props is the same as before
print(int(props))
