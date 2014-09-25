My status bar engine
====================

This is a status bar engine (surprise) made mainly for linux.  

It depends on (Arch packages):
* inotify-tools
* python3
* dzen[2]

For more information read [the wiki](https://github.com/ludat/SB/wiki)

This projected is licensed under the terms of the MIT license.

###Little warning

Although the engine doesn't need nothing anything else the individual widgets may.

The modules marked safe are safe for me but maybe not for you. I will check widgets that I should work everywhere:  
- [x] datetime: It justs uses python standard module `time`.
- [x] battery: Well you need a battery but if it's not there won't bother.
- [ ] network: It isn't ready for anyone
- [x] systemStatus: It just uses the `free` command so it should work everywhere
- [x] IP: It uses the `ip` command so it should work everywhere. (if you have `festival` working it will tell you that you are disconnected)
- [ ] volume: actualy it uses pulse audio so should rename it but if you use pulseaudio it should work
- [x] mpd: of course you need mpd running but it won't say much if you don't

You have been warned

TODO
----

* Write a lot of documentation
