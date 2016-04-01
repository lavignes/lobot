LoBot
=====

A highly extensible IRC Bot framework inspired by `irc3 <https://github.com/gawel/irc3>`_

.. image:: https://badge.fury.io/py/lobot.svg
    :target: https://badge.fury.io/py/lobot
    :alt: PyPI Version

.. image:: https://readthedocs.org/projects/lobot/badge/?version=latest
    :target: http://lobot.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/pyrated/lobot.svg?branch=master
    :target: https://travis-ci.org/pyrated/lobot
    :alt: Travis Build

Getting started
===============

::

    $ pip install lobot


Running LoBot
^^^^^^^^^^^^^

Start LoBot by passing it a working directory::

    $ lobot ~/.lobot


The first time you run LoBot, it will initialize the directory with a simple echo bot::

    bot-directory/
        config.json
        plugs/
            echo.py


Configuration
^^^^^^^^^^^^^

LoBot's configuration is in ``config.json``. The basic LoBot configuration is under the key ``lobot``::

    "lobot": {
        "nick": "LoBot",
        "username": "LoBot",
        "host": "irc.freenode.net",
        "port": 8001,
        "ssl": false,
        "channels": [
            "#lobot"
        ],
        "plugdir": "plugs",
        "plugins": [
            "echo"
        ]
    }


Documentation
=============

https://lobot.readthedocs.org

Requirements
============

- Python >= 3.5

License
=======

| Copyright (c) 2016 Scott LaVigne
|
| Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
|
| The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
|
| THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
