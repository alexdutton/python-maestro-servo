import struct

ServoStatus = struct.Struct("hhhb")
"""A struct for servo status.

For ChannelMode.servo:

* position
* target
* speed
* accelaration

For ChannelMode.input:

* _
* value
* _
* _

"""
