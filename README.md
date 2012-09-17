BitcoinArmory-Daemon
====================

BitcoinArmory-Daemon provides a <b>JSON-RPC interface</b> to Armory which is suitable for use on webservers and other instances where a GUI is not desired.

Installation
============


* Install dependencies (extra to armory dependencies).
* Download and extract the files.
* Copy your watch-only wallet to the same directory as you extracted the source.

How To Use
=======

Run

`$ python armory-daemon.py`

on the server from the directory the source was extracted to.

Now any client can access through jsonrpc. See [https://en.bitcoin.it/wiki/API_reference_(JSON-RPC)]
for examples of how to run a json-rpc client.

Dependencies
------------

<b>txjson-rpc<b>

`$ sudo pip install txJSON-RPC`

More info at [https://launchpad.net/txjsonrpc](https://launchpad.net/txjsonrpc)

[https://en.bitcoin.it/wiki/API_reference_(JSON-RPC)]: https://en.bitcoin.it/wiki/API_reference_(JSON-RPC) 