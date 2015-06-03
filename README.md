# PhotoBackup bottle server
The simplest PhotoBackup server, made with [bottle](http://bottlepy.org/) to
work with Python 3.


## Installation
First, build the virtual environment:

    make

Then run the installer, which asks for the directory to save your pictures to
and the server password:

    ./venv/bin/python install.py

The script looks for the directory to be writable by the typical `www-data` user.
It fails gracefully if it's not the case, just warning you to make it work properly.
This step creates a `photobackup_settings.py` file in the current directory.


## Usage
Launch the server with:

    ./venv/bin/python photobackup.py

By default, it runs on the host `0.0.0.0` and reloads automatically.
