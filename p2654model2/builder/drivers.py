#!/usr/bin/env python
"""
    Factory class used to manage the hardware drivers used by CONTROLLER building blocks.
    Copyright (C) 2021  Bradford G. Van Treuren

    Factory class used to manage the hardware drivers used by CONTROLLER building blocks.
    Call remove_drivers() when changing to a new model description to clear out old model
    references to old UUT hardware interfaces.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

__authors__ = ["Bradford G. Van Treuren"]
__contact__ = "bradvt59@gmail.com"
__copyright__ = "Copyright 2021, VT Enterprises Consulting Services"
__credits__ = ["Bradford G. Van Treuren"]
__date__ = "2021/03/05"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


from time import sleep

from drivers.ate.atesim import ATE, JTAGController, JTAGController2, GPIOController, I2CController, \
    SPIController


class Drivers(object):
    ate_inst = None
    jtag_inst = None
    jtag2_inst = None
    gpio_inst = None
    i2c_inst = None
    spi_inst = None
    board_sim = None

    @staticmethod
    def get_board_sim():
        return Drivers.board_sim

    @staticmethod
    def set_board_sim(board_sim):
        Drivers.board_sim = board_sim

    @staticmethod
    def get_ate():
        if Drivers.ate_inst is None:
            if Drivers.board_sim is None:
                raise AssertionError("Drivers board_sim must be defined before getting drivers.")
            ip = "127.0.0.1"
            port = 5023
            Drivers.ate_inst = ATE(ip=ip, port=port)
            sleep(0.05)
            Drivers.ate_inst.connect(Drivers.board_sim)
            sleep(0.05)
            while not Drivers.ate_inst.sim_status():
                sleep(0.05)
        return Drivers.ate_inst

    @staticmethod
    def get_jtag():
        if Drivers.jtag_inst is None:
            ate = Drivers.get_ate()
            Drivers.jtag_inst = JTAGController(ate)
            sleep(1)
        return Drivers.jtag_inst

    @staticmethod
    def get_jtag2():
        if Drivers.jtag2_inst is None:
            ate = Drivers.get_ate()
            Drivers.jtag2_inst = JTAGController2(ate)
            sleep(1)
        return Drivers.jtag2_inst

    @staticmethod
    def get_gpio():
        if Drivers.gpio_inst is None:
            ate = Drivers.get_ate()
            Drivers.gpio_inst = GPIOController(ate)
            sleep(1)
        return Drivers.gpio_inst

    @staticmethod
    def get_i2c():
        if Drivers.i2c_inst is None:
            ate = Drivers.get_ate()
            Drivers.i2c_inst = I2CController(ate)
            sleep(1)
        return Drivers.i2c_inst

    @staticmethod
    def get_spi():
        if Drivers.spi_inst is None:
            ate = Drivers.get_ate()
            Drivers.spi_inst = SPIController(ate)
            sleep(1)
        return Drivers.spi_inst

    @staticmethod
    def remove_drivers():
        Drivers.ate_inst = None
        Drivers.jtag1_inst = None
        Drivers.jtag2_inst = None
        Drivers.gpio_inst = None
        Drivers.i2c_inst = None
        Drivers.spi_inst = None
        Drivers.board_sim = None
