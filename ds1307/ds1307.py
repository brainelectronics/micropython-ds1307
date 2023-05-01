#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
I2C RTC driver for DS1307

https://github.com/mcauser/micropython-tinyrtc-i2c

MIT License
Copyright (c) 2018 Mike Causer
Extended 2023 by brainelectronics

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

BCD Format:
https://en.wikipedia.org/wiki/Binary-coded_decimal
"""

# system packages
from machine import I2C
try:
    from micropython import const
except ImportError:
    def const(x):
        return x


class _Subscriptable():
    def __getitem__(self, item):
        return None


_subscriptable = _Subscriptable()

Optional = _subscriptable
Tuple = _subscriptable

DATETIME_REG = const(0)     # 0x00-0x06
CHIP_HALT = const(128)
CONTROL_REG = const(7)      # 0x07
RAM_REG = const(8)          # 0x08-0x3F


class DS1307(object):
    """Driver for the DS1307 RTC."""

    def __init__(self, addr=0x68, i2c: Optional[I2C] = None) -> None:
        """
        Constructs a new instance

        :param      addr:   The I2C bus address of the EEPROM
        :type       addr:   int
        :param      i2c:    I2C object
        :type       i2c:    I2C
        """
        self._addr = addr

        if i2c is None:
            # default assignment, check the docs
            self._i2c = I2C(0)
        else:
            self._i2c = i2c

        self._weekday_start = 0
        self._halt = False

    @property
    def addr(self) -> int:
        """
        Get the DS1307 I2C bus address

        :returns:   DS1307 I2C bus address
        :rtype:     int
        """
        return self._addr

    @property
    def weekday_start(self) -> int:
        """
        Get the start of the weekday

        :returns:   Weekday start
        :rtype:     int
        """
        return self._weekday_start

    @weekday_start.setter
    def weekday_start(self, value: int) -> None:
        """Set the start of the weekday"""
        if 0 <= value <= 6:
            self._weekday_start = value
        else:
            raise ValueError("Weekday can only be in range 0-6")

    @property
    def datetime(self) -> Tuple[int, int, int, int, int, int, int, int]:
        """
        Get the current datetime

        (2023, 4, 18, 0, 10, 34, 4, 108)
        y,     m,  d, h, m,  s, wd, yd

        :returns:   (year, month, day, hour, minute, second, weekday, yearday)
        :rtype:     Tuple[int, int, int, int, int, int, int, int]
        """
        buf = bytearray(7)

        buf = self._i2c.readfrom_mem(self._addr, DATETIME_REG, 7)

        year = self._bcd_to_dec(buf[6]) + 2000
        month = self._bcd_to_dec(buf[5])
        day = self._bcd_to_dec(buf[4])
        yearday = self.day_of_year(year=year, month=month, day=day)
        return (
            year,
            month,
            day,
            self._bcd_to_dec(buf[2]),           # hour
            self._bcd_to_dec(buf[1]),           # minute
            self._bcd_to_dec(buf[0] & 0x7F),    # second
            self._bcd_to_dec(buf[3] - self._weekday_start),     # weekday
            yearday,
        )

    @datetime.setter
    def datetime(self, datetime: Tuple[int, int, int, int, int, int, int, int]) -> None:    # noqa: E501
        """
        Set datetime

        (2023, 4, 18, 20, 23, 38, 1, 108) by time.gmtime(time.time())
        y,     m,  d,  h, min,sec,wday, yday
        0,     1,  2,  3,  4,   5,   6, 7

        :param      datetime:  The datetime
        :type       datetime:  Tuple[int, int, int, int, int, int, int, int]
        """
        buf = bytearray(7)

        # msb = CH, 1 = halt, 0 = go
        buf[0] = self._dec_to_bcd(datetime[5]) & 0x7F   # second
        buf[1] = self._dec_to_bcd(datetime[4])  # minute
        buf[2] = self._dec_to_bcd(datetime[3])  # hour
        buf[3] = self._dec_to_bcd(datetime[6] + self._weekday_start)
        buf[4] = self._dec_to_bcd(datetime[2])  # day
        buf[5] = self._dec_to_bcd(datetime[1])  # month
        buf[6] = self._dec_to_bcd(datetime[0] - 2000)   # year

        if (self._halt):
            buf[0] |= (1 << 7)

        self._i2c.writeto_mem(self._addr, DATETIME_REG, buf)

    @property
    def year(self) -> int:
        """
        Get the year from the RTC

        :returns:   Year of RTC
        :rtype:     int
        """
        return self.datetime[0]

    @property
    def month(self) -> int:
        """
        Get the month from the RTC

        :returns:   Month of RTC
        :rtype:     int
        """
        return self.datetime[1]

    @property
    def day(self) -> int:
        """
        Get the day from the RTC

        :returns:   Day of RTC
        :rtype:     int
        """
        return self.datetime[2]

    @property
    def hour(self) -> int:
        """
        Get the hour from the RTC

        :returns:   Hour of RTC
        :rtype:     int
        """
        return self.datetime[3]

    @property
    def minute(self) -> int:
        """
        Get the minute from the RTC

        :returns:   Minute of RTC
        :rtype:     int
        """
        return self.datetime[4]

    @property
    def second(self) -> int:
        """
        Get the second from the RTC

        :returns:   Second of RTC
        :rtype:     int
        """
        return self.datetime[5]

    @property
    def weekday(self) -> int:
        """
        Get the weekday from the RTC

        :returns:   Weekday of RTC
        :rtype:     int
        """
        return self.datetime[5]

    @property
    def yearday(self) -> int:
        """
        Get the yearday from the RTC

        :returns:   Yearday of RTC
        :rtype:     int
        """
        return self.datetime[7]

    def is_leap_year(self, year: int) -> bool:
        """
        Determines whether the specified year is a leap year.

        :param      year:  The year
        :type       year:  int

        :returns:   True if the specified year is leap year, False otherwise.
        :rtype:     bool
        """
        return (year % 4 == 0)

    def day_of_year(self, year: int, month: int, day: int) -> int:
        """
        Get the day of the year

        :param      year:   The year
        :type       year:   int
        :param      month:  The month
        :type       month:  int
        :param      day:    The day
        :type       day:    int

        :returns:   Day of the year, January 1 is day 1
        :rtype:     int
        """
        month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        year -= 2000
        days16 = day

        for x in range(1, month):
            days16 += month_days[x - 1]

        if month >= 2 and self.is_leap_year(year=year):
            days16 += 1

        return days16

    @property
    def halt(self) -> bool:
        """
        Get status of DS1307

        :returns:   Status of DS1307
        :rtype:     bool
        """
        return self._halt

    @halt.setter
    def halt(self, value: bool = False) -> None:
        """
        Power up or power down the RTC oscillator

        :param      value:  The value
        :type       value:  bool
        """
        reg = self._i2c.readfrom_mem(self._addr, DATETIME_REG, 1)[0]

        if value:
            reg |= CHIP_HALT
        else:
            reg &= ~CHIP_HALT

        self._halt = bool(value)
        self._i2c.writeto_mem(self._addr, DATETIME_REG, bytearray([reg]))

    def square_wave(self, sqw: int = 0, out: int = 0) -> None:
        """
        Output square wave on pin SQ

        at 1Hz, 4.096kHz, 8.192kHz or 32.768kHz, or disable the oscillator
        and output logic level high/low.
        """
        if sqw not in (0, 1, 4, 8, 32):
            raise ValueError(
                "Squarewave can be set to 0Hz, 1Hz, {}Hz, {}Hz or {}Hz".format(
                    2 ** 12, 2 ** 13, 2 ** 15)
            )

        rs0 = 1 if sqw == 4 or sqw == 32 else 0
        rs1 = 1 if sqw == 8 or sqw == 32 else 0
        out = 1 if out > 0 else 0
        sqw = 1 if sqw > 0 else 0

        reg = rs0 | rs1 << 1 | sqw << 4 | out << 7

        self._i2c.writeto_mem(self._addr, CONTROL_REG, bytearray([reg]))

    def _dec_to_bcd(self, value: int) -> int:
        """
        Convert decimal to binary coded decimal (BCD) format

        :param      value:  The value
        :type       value:  int

        :returns:   Binary coded decimal (BCD) format
        :rtype:     int
        """
        return (value // 10) << 4 | (value % 10)

    def _bcd_to_dec(self, value: int) -> int:
        """
        Convert binary coded decimal (BCD) format to decimal

        :param      value:  The value
        :type       value:  int

        :returns:   Decimal value
        :rtype:     int
        """
        return ((value >> 4) * 10) + (value & 0x0F)
