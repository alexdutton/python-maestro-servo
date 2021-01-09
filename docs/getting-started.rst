Getting started
===============

Before you can get started coding, ensure you've performed all the steps in :doc:`installation`, including the step
about configuring udev.

You should also read the `Pololu Maestro Servo Controller User’s Guide <https://www.pololu.com/docs/0J40>`_, as the
concepts documented there correspond to functionality exposed through this Python module.

Assuming you're getting started with a single controller, plug it in and try the following:

.. code-block:: python

   from maestro import Maestro

   maestro = Maestro.get_one()

   print("Maestro:", maestro)
   print("Channel count:", maestro.channel_count)

You should get something like:

.. code-block::

   Maestro: <maestro.device.MiniMaestro "00262773">
   Channel count: 12

The :py:class:`maestro.Meastro` instance provides a list-like interface for accessing channels, so we can iterate over
all the channels, or get one by index (starting at channel 0):

.. code-block:: python

   print("All channels:", list(maestro))
   print("The third channel:", maestro[2])

And the result:

.. code-block::

   All channels: [<maestro.channel.Channel 0: Servo>, <maestro.channel.Channel 1: Servo>, <maestro.channel.Channel 2: Servo>, <maestro.channel.Channel 3: Servo>, <maestro.channel.Channel 4: Input>, <maestro.channel.Channel 5: Input>, <maestro.channel.Channel 6: Input>, <maestro.channel.Channel 7: Input>, <maestro.channel.Channel 8: Input>, <maestro.channel.Channel 9: Input>, <maestro.channel.Channel 10: Input>, <maestro.channel.Channel 11: Input>]
   The third channel: <maestro.channel.Channel 2: Servo>

Using a channel as a servo
--------------------------

A channel
