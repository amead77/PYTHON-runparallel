# PYTHON-runparallel
## created specifically to run mp3gain on lots of files in windows. probably won't be updated

At some point maybe 6 years ago, I needed to adjust the gain on all my mp3s. Not a quick task as mp3gain and the windows frontend was single threaded.
What this code does is ask you to split the files into groups (1..corecount). It then copies or moves them, before running mp3gain on the lot.
Did what I needed, but was a cludge as I struggled to get a viable pure python version working. Instead it cheats by using windows own "start /affinity <cpuaffinity> <cmd>"
This works, provided you intend to use <= 8 cores as I never hardcoded any other cores.
Considerably faster than running mp3gain in series, will completely saturate your cpu usage.
