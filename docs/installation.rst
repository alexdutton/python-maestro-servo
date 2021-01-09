Installation
============

You can install this library `from PyPI <https://pypi.org/project/maestro-servo/>`_:

.. code-block:: shell

   $ pip install maestro-servo


Maestro USB device access on Linux
----------------------------------

When you connect a Maestro (or any USB device), udev is used to manage access
permissions. There are no rules for Maestro devices distributed with udev, so by default
only the root user can access the device. Before you can access your Maestro device as a normal user, you will need to
create some udev rules.

You'll need a file in `/etc/udev/rules.d/`, e.g. `/etc/udev/rules.d/10-pololu.rules` containing the following:

.. code-block::

   SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1ffb", ATTRS{idProduct}=="0089", TAG+="uaccess"
   SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1ffb", ATTRS{idProduct}=="008a", TAG+="uaccess"
   SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1ffb", ATTRS{idProduct}=="008b", TAG+="uaccess"
   SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1ffb", ATTRS{idProduct}=="008c", TAG+="uaccess"

This ensures that the currently-logged-in user on a desktop machine is able to access the device.

Once this is done, you're all set.