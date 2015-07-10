# PhotoBackup bottle server
The simplest PhotoBackup server, made with [bottle](http://bottlepy.org/) to
work with [Python 3](https://www.python.org/). It follows the
[official API](https://github.com/PhotoBackup/api/blob/master/api.raml).

## Installation
First, build the virtual environment:

    make

Then run the installer, which asks for the directory to save your pictures to
and the server password:

    ./venv/bin/python install.py

The script looks for the directory to be writable by the usual `www-data` user.
It fails gracefully if it is not, just warning you to make it work properly.
This step creates a `photobackup_settings.py` file in the current directory.


## Usage
Launch the server with:

    ./venv/bin/python photobackup.py

By default, it runs on host `0.0.0.0` and reloads automatically.


## Production
To put in production, use something like [gunicorn](http://gunicorn.org/)
behind your webserver.
