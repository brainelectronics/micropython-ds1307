# MicroPython DS1307

[![Downloads](https://pepy.tech/badge/micropython-ds1307)](https://pepy.tech/project/micropython-ds1307)
![Release](https://img.shields.io/github/v/release/brainelectronics/micropython-ds1307?include_prereleases&color=success)
![MicroPython](https://img.shields.io/badge/micropython-Ok-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/github/brainelectronics/micropython-ds1307/branch/main/graph/badge.svg)](https://app.codecov.io/github/brainelectronics/micropython-ds1307)
[![CI](https://github.com/brainelectronics/micropython-ds1307/actions/workflows/release.yml/badge.svg)](https://github.com/brainelectronics/micropython-ds1307/actions/workflows/release.yml)

MicroPython driver for DS1307 RTC

---------------

## General

MicroPython driver for DS1307 RTC

📚 The latest documentation is available at
[MicroPython DS1307 ReadTheDocs][ref-rtd-micropython-ds1307] 📚

<!-- MarkdownTOC -->

- [Installation](#installation)
	- [Install required tools](#install-required-tools)
- [Setup](#setup)
	- [Install package with upip](#install-package-with-upip)
		- [General](#general)
		- [Specific version](#specific-version)
		- [Test version](#test-version)
	- [Manually](#manually)
		- [Upload files to board](#upload-files-to-board)
- [Usage](#usage)
- [Contributing](#contributing)
	- [Unittests](#unittests)
- [Credits](#credits)

<!-- /MarkdownTOC -->

## Installation

### Install required tools

Python3 must be installed on your system. Check the current Python version
with the following command

```bash
python --version
python3 --version
```

Depending on which command `Python 3.x.y` (with x.y as some numbers) is
returned, use that command to proceed.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Setup

### Install package with upip

Connect the MicroPython device to a network (if possible)

```python
import network
station = network.WLAN(network.STA_IF)
station.connect('SSID', 'PASSWORD')
station.isconnected()
```

#### General

Install the latest package version of this lib on the MicroPython device

```python
import mip
mip.install("github:brainelectronics/micropython-ds1307")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`

```python
import upip
upip.install('micropython-ds1307')
```

#### Specific version

Install a specific, fixed package version of this lib on the MicroPython device

```python
import mip
# install a verions of a specific branch
mip.install("github:brainelectronics/micropython-ds1307", version="feature/initial-implementation")
# install a tag version
mip.install("github:brainelectronics/micropython-ds1307", version="0.1.0")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`

```python
import upip
upip.install('micropython-ds1307')
```

#### Test version

Install a specific release candidate version uploaded to
[Test Python Package Index](https://test.pypi.org/) on every PR on the
MicroPython device. If no specific version is set, the latest stable version
will be used.

```python
import mip
mip.install("github:brainelectronics/micropython-ds1307", version="0.1.0-rc1.dev1")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`

```python
import upip
# overwrite index_urls to only take artifacts from test.pypi.org
upip.index_urls = ['https://test.pypi.org/pypi']
upip.install('micropython-ds1307')
```

See also [brainelectronics Test PyPi Server in Docker][ref-brainelectronics-test-pypiserver]
for a test PyPi server running on Docker.

### Manually

#### Upload files to board

Copy the module to the MicroPython board and import them as shown below
using [Remote MicroPython shell][ref-remote-upy-shell]

Open the remote shell with the following command. Additionally use `-b 115200`
in case no CP210x is used but a CH34x.

```bash
rshell --port /dev/tty.SLAB_USBtoUART --editor nano
```

Perform the following command inside the `rshell` to copy all files and
folders to the device

```bash
mkdir /pyboard/lib
mkdir /pyboard/lib/ds1307

cp ds1307/* /pyboard/lib/ds1307

cp examples/main.py /pyboard
cp examples/boot.py /pyboard
```

## Usage

```python
from eeprom import DS1307
from machine import I2C, Pin
from time import gmtime

I2C_ADDR = 0x68

# define custom I2C interface, default is 'I2C(0)'
# check the docs of your device for further details and pin infos
# this are the pins for the Raspberry Pi Pico adapter board
i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=800000)
ds1307 = DS1307(addr=I2C_ADDR, i2c=i2c)   # DS1307 on 0x68

# get the current RTC time
print("Current RTC time: {}".format(ds1307.datetime))

# set the RTC time to the current system time
now = gmtime(time())
ds1307.datetime = now

print("Current RTC time: {}".format(ds1307.datetime))

# Print the date and time in ISO8601 format: 2023-04-18T21:14:22
print("Today is {:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
    ds1307.year, ds1307.month, ds1307.day,
    ds1307.hour, ds1307.minute, ds1307.second))
```

## Contributing

### Unittests

Run the unittests locally with the following command after installing this
package in a virtual environment

```bash
# run all tests
nose2 --config tests/unittest.cfg

# run only one specific tests
nose2 tests.test_ds1307.TestDS1307.test_addr
```

Generate the coverage files with

```bash
python create_report_dirs.py
coverage html
```

The coverage report is placed at `reports/coverage/html/index.html`

## Credits

Based on
[Mike Causer's MicroPython TinyRTC I2C module][ref-micropython-tinyrtc-i2c]
and the [PyPa sample project][ref-pypa-sample]

<!-- Links -->
[ref-rtd-micropython-ds1307]: https://micropython-ds1307.readthedocs.io/en/latest/
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
[ref-brainelectronics-test-pypiserver]: https://github.com/brainelectronics/test-pypiserver
[ref-micropython-tinyrtc-i2c]: https://github.com/mcauser/micropython-tinyrtc-i2c
[ref-pypa-sample]: https://github.com/pypa/sampleproject
[ref-test-pypi]: https://test.pypi.org/
[ref-pypi]: https://pypi.org/
