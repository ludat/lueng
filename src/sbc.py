#!/bin/env python3
import socket
import os

print("Connecting...")
if os.path.exists("/tmp/SB"):
    print("Ready.")
    print("Ctrl-C to quit.")
    print("Sending 'DONE' shuts down the server and quits.")
    while True:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect("/tmp/SB")
        try:
            x = input("> ")
            if "" != x:
                print("SEND:", x)
                client.sendall(x.encode('utf-8'))
                if "DONE" == x:
                    print("Shutting down.")
                    break
            print("Recived: " + client.recv(1024).decode('utf-8'))
        except KeyboardInterrupt as k:
            print("Shutting down.")
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            break
        client.close()
else:
    print("Couldn't Connect!")
    print("Done")
