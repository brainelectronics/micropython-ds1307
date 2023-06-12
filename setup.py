#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from setuptools import setup
from pathlib import Path
import sdist_upip

here = Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# load elements of version.py
exec(open(here / 'ds1307' / 'version.py').read())

setup(
    name='micropython-ds1307',
    version=__version__,
    description="MicroPython driver for DS1307 RTC",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/brainelectronics/micropython-ds1307',
    author='brainelectronics',
    author_email='info@brainelectronics.de',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: Implementation :: MicroPython',
    ],
    keywords='micropython, i2c, ds1307, driver',
    project_urls={
        'Bug Reports': 'https://github.com/brainelectronics/micropython-ds1307/issues',
        'Source': 'https://github.com/brainelectronics/micropython-ds1307',
    },
    license='MIT',
    cmdclass={'sdist': sdist_upip.sdist},
    packages=['ds1307'],
    install_requires=[]
)
