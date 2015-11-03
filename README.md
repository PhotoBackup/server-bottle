#  The Python PhotoBackup server implementation 

The Python3 implementation of PhotoBackup server, made with
[bottle](http://bottlepy.org/). It follows the
[official API](https://github.com/PhotoBackup/api/blob/master/api.raml), currently in [version 2](https://github.com/PhotoBackup/api/releases/tag/v2).

## Installation

Install through [PyPI](https://pypi.python.org/pypi):

    pip install photobackup_bottle

Then run the installer, which asks for the directory to save your pictures to
and the server password:

    photobackup init

The script looks for the directory to be writable by the usual `www-data` user.
It fails gracefully if it is not, just warning you to make it work properly.
This step creates a `.photobackup` file in the user's home directory,
containing:

* `BindAddress`, the IP address (default is `127.0.0.1`) ;
* `MediaRoot`, the directory where the pictures are written in ;
* `Password`, the SHA-512 hashed password ;
* `PasswordBcrypt`, a Bcrypt-ed version of your SHA-512 hashed password ;
* `Port`, the port (default is `8420`).

## Usage

Launch the server with:

    photobackup run

By default, it runs on host `127.0.0.1`, port `8420` and reloads automatically.

## Production

To put in production, use [Nginx](http://nginx.org/) to bind a sever name to `http://127.0.0.1:8420`.
