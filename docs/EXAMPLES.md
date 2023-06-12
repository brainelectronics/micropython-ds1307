# Examples

Usage examples of this `micropython-ds1307` library

---------------

## General

An example of all implemented functionalities can be found at the
[MicroPython DS1307 examples folder][ref-micropython-ds1307-examples]

## Setup DS1307

```python
from ds1307 import DS1307
from machine import I2C, Pin

# DS1307 on 0x68
I2C_ADDR = 0x68     # DEC 104, HEX 0x68

# define custom I2C interface, default is 'I2C(0)'
# check the docs of your device for further details and pin infos
# this are the pins for the Raspberry Pi Pico adapter board
i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=800000)
ds1307 = DS1307(addr=I2C_ADDR, i2c=i2c)

# get LCD infos/properties
print("DS1307 is on I2C address 0x{0:02x}".format(ds1307.addr))
print("Weekday start is {}".format(ds1307.weekday_start))
```

## Set time

Set the RTC time to the current system time

```python
from time import gmtime, time

now = gmtime(time())
ds1307.datetime = now
```

## Get time

Get the current RTC time and all available properties of `DS1307`

```python
# Print the date and time in ISO8601 format: 2023-04-18T21:14:22
print("Today is {:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
    ds1307.year, ds1307.month, ds1307.day,
    ds1307.hour, ds1307.minute, ds1307.second))

# check whether this year is a leap year
print("Is this year a leap year? {}".format(ds1307.is_leap_year(ds1307.year)))

# get the day of the year
print("Today is day {} of {}".format(
    ds1307.day_of_year(year=ds1307.year, month=ds1307.month, day=ds1307.day),
    ds1307.year))
```

## Oscillator

Interact with the oscillator of the RTC

```python
from time import sleep

print("The oscillator is currently active at {}? {}".format(
    ds1307.datetime, ds1307.halt))
print("Halt the oscillator and wait for 5 seconds ...")
ds1307.halt = True
sleep(5)

print("Current RTC time: {}".format(ds1307.datetime))

print("Enable the oscillator and wait for 5 seconds ...")
ds1307.halt = False
sleep(5)
print("Current RTC time: {}".format(ds1307.datetime))
```

## Square Wave Pin

Control the squarewave pin `SQ`

```python
from time import sleep

print("Set square wave output to 1Hz and wait for 5 seconds ...")
ds1307.square_wave(sqw=1)
sleep(5)

print("Set square wave output to 4.096kHz and wait for 5 seconds ...")
ds1307.square_wave(sqw=4)
sleep(5)

print("Set square wave output to 8.192kHz and wait for 5 seconds ...")
ds1307.square_wave(sqw=8)
sleep(5)

print("Set square wave output to HIGH and wait for 5 seconds ...")
ds1307.square_wave(out=1)
sleep(5)

print("Set square wave output to LOW and wait for 5 seconds ...")
ds1307.square_wave(sqw=0)
sleep(5)
```

[ref-micropython-ds1307-examples]: https://github.com/brainelectronics/micropython-ds1307/tree/main/examples
