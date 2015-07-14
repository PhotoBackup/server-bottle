# PhotoBackup Python server

The Python3 implementation of PhotoBackup server, made with
[bottle](http://bottlepy.org/). It follows the
[official API](https://github.com/PhotoBackup/api/blob/master/api.raml).

## Installation

Install through [PyPI](https://pypi.python.org/pypi):

    pip install photobackup_bottle

Then run the installer, which asks for the directory to save your pictures to
and the server password:

    photobackup init

The script looks for the directory to be writable by the usual `www-data` user.
It fails gracefully if it is not, just warning you to make it work properly.
This step creates a `photobackup_settings.py` file in the current directory,
containing:

* `MEDIA_ROOT`, the directory where the pictures are written in ;
* `PASSWORD`, the SHA-512 hashed password ;
* `PORT`, the port (default is 8420).

## Usage

Launch the server with:

    photobackup run

By default, it runs on host `0.0.0.0`, port `8420` and reloads automatically.

## Production

To put in production, use something like [gunicorn](http://gunicorn.org/)
behind your webserver.
