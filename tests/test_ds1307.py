#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Unittest for MicroPython DS1307"""

import logging
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

from nose2.tools import params


class Pin(object):
    """Fake MicroPython Pin class"""
    def __init__(self, pin: int, mode: int = -1):
        self._pin = pin
        self._mode = mode
        self._value = 0


class I2C(object):
    """Fake MicroPython I2C class"""
    def __init__(self, id: int, *, scl: Pin, sda: Pin, freq: int = 400000):
        self._id = id
        self._scl = scl
        self._sda = sda
        self._freq = freq

    def writeto(addr: int, buf: bytearray, stop: bool = True) -> int:
        return 1

    def readfrom_mem(addr: int,
                     memaddr: int,
                     nbytes: int,
                     *,
                     addrsize: int = 8) -> int:
        return 1

    def writeto_mem(addr: int,
                    memaddr: int,
                    buf: bytearray,
                    *,
                    addrsize: int = 8):
        pass


# custom imports
sys.modules['machine.I2C'] = I2C
to_be_mocked = [
    'machine',
    'time.sleep_ms', 'time.sleep_us',
]
for module in to_be_mocked:
    sys.modules[module] = Mock()

from ds1307 import DS1307  # noqa: E402


class TestDS1307(unittest.TestCase):
    """This class describes a TestDS1307 unittest."""

    def setUp(self) -> None:
        """Run before every test method"""
        # define a format
        custom_format = "[%(asctime)s][%(levelname)-8s][%(filename)-20s @" \
                        " %(funcName)-15s:%(lineno)4s] %(message)s"

        # set basic config and level for all loggers
        logging.basicConfig(level=logging.INFO,
                            format=custom_format,
                            stream=sys.stdout)

        # create a logger for this TestSuite
        self.test_logger = logging.getLogger(__name__)

        # set the test logger level
        self.test_logger.setLevel(logging.DEBUG)

        # enable/disable the log output of the device logger for the tests
        # if enabled log data inside this test will be printed
        self.test_logger.disabled = False

        self.i2c = I2C(1, scl=Pin(13), sda=Pin(12), freq=800_000)
        self._calls_counter: int = 0
        self._tracked_call_data: list = []
        self._mocked_read_data: bytes = b''
        self.ds1307 = DS1307()

    def _tracked_call(self, *args, **kwargs) -> None:
        """Track function calls and the used arguments"""
        self._tracked_call_data.append({'args': args, 'kwargs': kwargs})

    def test_init(self) -> None:
        """Test DS1307 init function"""
        ds1307 = DS1307()
        self.assertEqual(ds1307.addr, 0x68)
        # self.assertEqual(ds1307._i2c._id, 0)

        ds1307 = DS1307(i2c=self.i2c)
        self.assertEqual(ds1307.addr, 0x68)
        self.assertEqual(ds1307._i2c._id, 1)

    @params(
        (0x68),
        (104),
    )
    def test_addr(self, addr: int) -> None:
        """Test address property"""
        ds1307 = DS1307(addr=addr)

        self.assertEqual(ds1307.addr, addr)

    def test_weekday_start(self) -> None:
        """Test weekday property"""
        self.assertEqual(self.ds1307.weekday_start, 0)

        # test valid weekday start
        self.ds1307.weekday_start = 1
        self.assertEqual(self.ds1307.weekday_start, 1)

        # test invalid weekday start
        for day in [-1, 7]:
            with self.assertRaises(ValueError) as context:
                self.ds1307.weekday_start = day

            self.assertEqual(
                str(context.exception),
                "Weekday can only be in range 0-6"
            )

    @patch.object(I2C, 'readfrom_mem')
    def test_datetime(self, mock_readfrom_mem: MagicMock) -> None:
        """Test datetime property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 3, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(
            ds1307.datetime,
            (2023, 5, 29, 20, 45, 59, 3, 149)
        )

        with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
            ds1307.datetime = (2023, 5, 29, 20, 45, 59, 3, 149)

            self.assertEqual(len(self._tracked_call_data), 1)
            self.assertEqual(
                self._tracked_call_data[0]['args'],
                (ds1307.addr, 0, buf)
            )

    @patch.object(I2C, 'readfrom_mem')
    def test_year(self, mock_readfrom_mem: MagicMock) -> None:
        """Test year property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 3, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.year, 2023)

    @patch.object(I2C, 'readfrom_mem')
    def test_month(self, mock_readfrom_mem: MagicMock) -> None:
        """Test month property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 3, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.month, 5)

    @patch.object(I2C, 'readfrom_mem')
    def test_day(self, mock_readfrom_mem: MagicMock) -> None:
        """Test day property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 3, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.day, 29)

    @patch.object(I2C, 'readfrom_mem')
    def test_hour(self, mock_readfrom_mem: MagicMock) -> None:
        """Test hour property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 3, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.hour, 20)

    @patch.object(I2C, 'readfrom_mem')
    def test_minute(self, mock_readfrom_mem: MagicMock) -> None:
        """Test minute property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 3, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.minute, 45)

    @patch.object(I2C, 'readfrom_mem')
    def test_second(self, mock_readfrom_mem: MagicMock) -> None:
        """Test second property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 3, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.second, 59)

    @patch.object(I2C, 'readfrom_mem')
    def test_weekday(self, mock_readfrom_mem: MagicMock) -> None:
        """Test weekday property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 0, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.weekday, 59)

    @patch.object(I2C, 'readfrom_mem')
    def test_yearday(self, mock_readfrom_mem: MagicMock) -> None:
        """Test yearday property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 0, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.yearday, 149)

    @patch.object(I2C, 'readfrom_mem')
    def test_is_leap_year(self, mock_readfrom_mem: MagicMock) -> None:
        """Test leap year property"""
        ds1307 = DS1307(i2c=self.i2c)

        # 2023-05-29T20:45:59
        #                0,  1,  2, 3,  4,  5, 6
        #                s,  m,  h, wd, d,  m, y
        buf = bytearray([89, 69, 32, 0, 41, 5, 35])
        mock_readfrom_mem.return_value = buf

        self.assertEqual(ds1307.is_leap_year(2023), False)
        self.assertEqual(ds1307.is_leap_year(2024), True)

    def test_day_of_year(self) -> None:
        """Test day of year"""
        self.assertEqual(
            self.ds1307.day_of_year(year=2023, month=5, day=29),
            149
        )
        self.assertEqual(
            self.ds1307.day_of_year(year=2024, month=3, day=26),
            86
        )

    @patch.object(I2C, 'readfrom_mem')
    def test_halt(self, mock_readfrom_mem: MagicMock) -> None:
        """Test power up/down of RTC"""
        ds1307 = DS1307(i2c=self.i2c)

        self.assertFalse(ds1307.halt)

        for halt, buf, expectation in zip(
            [True, True, False, False],
            [
                # 2023-05-29T20:45:59
                [89, 69, 32, 0, 41, 5, 35],
                # 2023-05-29T20:46:00
                [0, 70, 32, 0, 41, 5, 35],
                # 2023-05-29T20:45:59
                [89, 69, 32, 0, 41, 5, 35],
                # 2023-05-29T20:46:00
                [0, 70, 32, 0, 41, 5, 35]
            ],
                [0xd9, 0x80, 0x59, 0x0]):
            with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
                mock_readfrom_mem.return_value = buf
                ds1307.halt = halt

                self.assertEqual(len(self._tracked_call_data), 1)
                self.assertEqual(
                    self._tracked_call_data[0]['args'],
                    (ds1307.addr, 0, bytearray([expectation]))
                )
                self._tracked_call_data = []

    def test_square_wave(self) -> None:
        """Test setting square wave output pin"""
        with self.assertRaises(ValueError) as context:
            self.ds1307.square_wave(sqw=2)

        self.assertEqual(
            str(context.exception),
            "Squarewave can be set to 0Hz, 1Hz, 4096Hz, 8192Hz or 32768Hz"
        )

        ds1307 = DS1307(i2c=self.i2c)

        for sqw, expectation in zip((0, 1, 4, 8, 32),
                                    (0x80, 0x90, 0x91, 0x92, 0x93)):
            with patch.object(I2C, 'writeto_mem', wraps=self._tracked_call):
                ds1307.square_wave(sqw=sqw, out=1)

            self.assertEqual(len(self._tracked_call_data), 1)
            self.assertEqual(
                self._tracked_call_data[0]['args'],
                (ds1307.addr, 7, bytearray([expectation]))
            )
            self._tracked_call_data = []

    def test__dec_to_bcd(self) -> None:
        """Test converting decimal to BCD"""
        self.assertEqual(self.ds1307._dec_to_bcd(value=1), 1)
        self.assertEqual(self.ds1307._dec_to_bcd(value=5), 5)
        self.assertEqual(self.ds1307._dec_to_bcd(value=10), 16)
        self.assertEqual(self.ds1307._dec_to_bcd(value=11), 17)
        self.assertEqual(self.ds1307._dec_to_bcd(value=300), 480)

    def test__bcd_to_dec(self) -> None:
        """Test converting BCD to decimal"""
        self.assertEqual(self.ds1307._bcd_to_dec(value=1), 1)
        self.assertEqual(self.ds1307._bcd_to_dec(value=5), 5)
        self.assertEqual(self.ds1307._bcd_to_dec(value=26), 20)
        self.assertEqual(self.ds1307._bcd_to_dec(value=2023), 1267)

    def tearDown(self) -> None:
        """Run after every test method"""
        pass


if __name__ == '__main__':
    unittest.main()
