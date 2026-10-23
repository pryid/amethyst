<img align="left" width="100" height="100" src="logo.png" alt="logo" style="float: left;"/>

<h3 align="left">Amethyst. <br>iOS 12/13 jailbreak for all devices<div align="right" style="float: top;">
</br></h3> 

# Information:
- Guide for installing is available at [ios.cfw.guide](https://ios.cfw.guide/installing-amethyst)
- There is no warranty with this software, so use at your own risk.

# Diagnostic logging

This fork saves stdout, stderr and progress messages to a new file in
`Documents/AmethystLogs` before the app UI starts. Each session records the app
version, device model, iOS version and uptime; attempts also record the selected
method/settings and the return code when `run_jailbreak` returns.

Long-press the **Amethyst** title to share the most recent eight log files.
Export a log once before rebooting to verify that saving and sharing work.
Then fully reboot, open this app and start the attempt manually. If the phone
reboots during an attempt, reopen the app and export the previous session's log.
If logging initialization fails, the Jailbreak button reports the error instead
of starting an attempt without a log.

Logs stay in the app's container; deleting the app deletes its logs. A newly
signed installation may use a different container and settings. Logging changes
I/O timing, and the last writes can still be lost during a panic or power loss.

The C logger can be tested on Linux or macOS without executing the jailbreak:

```sh
python3 -m unittest discover -s tests -v
```

# Credits:
- [staturnz](https://github.com/staturnzz) - Main Developer
- [Alfie CG](https://github.com/alfiecg24) - Trigon
- [Clarity](https://github.com/TheRealClarity) - Various techniques
- [xerus](https://x.com/xerusdesign) - Logo, Icon, Designs
- [felix-pb](https://github.com/felix-pb) - puaf_physpuppet
- [opa334](https://github.com/opa334) - Various techniques
- [xerub](https://github.com/xerub) - Patchfinder base
- [oct0xor](https://github.com/oct0xor), [kucher1n](https://x.com/kucher1n), [bzvr_](https://x.com/bzvr_), et el. - Operation Triangulation
- [Procursus](https://github.com/ProcursusTeam) - Bootstrap
- [Zebra Team](https://github.com/zbrateam) - Zebra
- [Sileo Team](https://github.com/Sileo) - Sileo
