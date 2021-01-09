# Maestro server controller library

This library aims to support [Pololu's USB servo
controllers](https://www.pololu.com/category/102/maestro-usb-servo-controllers), but doesn't do much yet, as it's still
in development and the author doesn't have any servos yet.

It can currently:

* read input values

Things yet to be implemented:

* actually controlling servos
* configuring channels to be input/output/servos

It has only been tested with a Mini Maestro 12. The existing functionality should work with the 18 and 24, but the Micro
Maestro is rather different, and would need more work.

Pull requests or other interest in co-development very welcome!

## udev rules

You'll need a file in `/etc/udev/rules.d/`, e.g. `/etc/udev/rules.d/10-pololu.rules` containing the following:

```udev
SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1ffb", ATTRS{idProduct}=="0089", GROUP="plugdev"
SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1ffb", ATTRS{idProduct}=="008a", GROUP="plugdev"
SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1ffb", ATTRS{idProduct}=="008b", GROUP="plugdev"
SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1ffb", ATTRS{idProduct}=="008c", GROUP="plugdev"
```

For RedHat or Fedora-based distros you should use the `dialout` group instead of `plugdev`. You should add yourself to
that group with e.g.:

```shell
$ sudo usermod -a -G plugdev YOUR_USERNAME
```
