import time
import unittest

from maestro import Maestro
from maestro.enums import ChannelMode, USCParameter


class DeviceTestCase(unittest.TestCase):
    def test_get_one(self):
        maestro = Maestro.get_one()
        maestro.clear_errors()

        for i in range(4):
            print("Mode", maestro[i].mode)
            maestro[i].mode = ChannelMode.Servo

        maestro.reinitialize()

        for i in range(4):
            maestro[i].target = 2000
            time.sleep(1)

        maestro.refresh_values()

        for i in range(4):
            print("Target", maestro[i].target, maestro[i].position)
