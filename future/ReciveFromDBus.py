#! /bin/env python3
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject

def vpn_connection_handler(*args, **keywords):
    # args = args[0]
    print("**"*50)
    print(len(args))
    print(args)
    print("--"*50)
    print(keywords)
    

DBusGMainLoop(set_as_default=True)
system_bus = dbus.SystemBus()

system_bus.add_signal_receiver(vpn_connection_handler,
        destination_keyword = "destination",
        interface_keyword = "interface",
        member_keyword = "member",
        path_keyword = "path",
        message_keyword = "message")

loop = GObject.MainLoop()
loop.run()
