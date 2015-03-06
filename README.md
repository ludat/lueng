My status bar engine
====================

This is a status bar engine (surprise) made mainly for linux but it should run on any Unix-like OS.

It depends on (Arch packages):
* python3
* dzen[2]

For more information read [the wiki](https://github.com/ludat/lueng/wiki)

**Warning: this is now (6/3/15) very outdated.** As soon as I end this refactoring I'll update the wiki

This projected is licensed under the terms of the MIT license.

###Little warning

Although the engine doesn't need nothing anything else the individual widgets may.

The modules marked safe are safe for me but maybe not for you. I will check widgets that I should work everywhere:
- [x] datetime: It justs uses python standard module `time`.
- [x] battery: Well you need a battery but if it's not there it won't do much
- [ ] network: It isn't ready for anyone and probably will never be
- [x] systemStatus: It just parses the `/proc/meminfo` file so it should work everywhere although I experienced some truble after a kernel upgrade some time ago
- [x] IP: It uses the `ip` command so it should work everywhere. (if you have `festival` working it will tell you when you lose or gain connectivity based on your current ip)
- [ ] paVolume: obviusly it needs a PulseAudio server to connect to and since it uses the external command `pactl` it will crash if it's not installed
- [x] mpd: of course you need mpd running but it won't say much if you don't

You have been warned

TODO
----

* Write a lot of documentation
