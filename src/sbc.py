#!/bin/env python3
import socket
import os

print("Connecting...")
if os.path.exists("/tmp/SB"):
    print("Ctrl-C to quit.")
    while True:
        try:
            x = input("> ")
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect("/tmp/SB")
            if "" != x:
                client.sendall(x.encode('utf-8'))
            print(client.recv(1024).decode('utf-8'))
        except ConnectionRefusedError as e:
            print(str(e))
        except KeyboardInterrupt as k:
            print("Shutting down.")
            client.shutdown(socket.SHUT_RDWR)
            break
        finally:
            client.close()
else:
    print("Couldn't Connect!")
