#!/bin/env python3

import select
import subprocess

epoll = select.epoll()
p1 = subprocess.Popen("echo hello", stdout=subprocess.PIPE, universal_newlines=True, shell=True)
p2 = subprocess.Popen("echo hi", stdout=subprocess.PIPE, universal_newlines=True, shell=True)

epoll.register(p1.stdout)
epoll.register(p2.stdout)

print(epoll.poll())
print(p1.stdout.read())

print(epoll.poll())
print(p1.stdout.read(),)
