#!/usr/bin/env python
# Copyright (C) 2013-2015 Stéphane Péchard.
#
# This file is part of PhotoBackup.
#
# PhotoBackup is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PhotoBackup is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""PhotoBackup Python server.

Usage:
  photobackup init
  photobackup run
  photobackup (-h | --help)
  photobackup --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# stlib
import configparser
import os
import sys
# pipped
import bcrypt
from bottle import abort, redirect, request, route, run
import bottle
from docopt import docopt
from logbook import info, warn, error
# local
from . import __version__, init


def init_config():
    """ Launch init.py script to create configuration file on user's disk. """
    init.init()
    sys.exit("\nCreated, now launch PhotoBackup server with 'photobackup run'")


def read_config():
    """ Set configuration file data into local dictionnary. """
    filename = os.path.expanduser("~/.photobackup")
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option  # to keep case of keys
    try:
        config.read_file(open(filename))
    except OSError:
        error("can't read configuration file, running 'photobackup init'")
        init_config()

    # Check if all keys are in the file
    keys = ['BindAddress', 'MediaRoot', 'Password', 'PasswordBcrypt', 'Port']
    for key in keys:
        if key not in config['photobackup']:
            error("config file incomplete, please regenerate!")
            init_config()
    return config['photobackup']


def end(code, message):
    error(message)
    abort(code, message)


def validate_password(request, isTest = False):
    password = request.forms.get('password').encode('utf-8')

    if 'PasswordBcrypt' in config:
        passcrypt = config['PasswordBcrypt'].encode('utf-8')
        if bcrypt.hashpw(password, passcrypt) != passcrypt:
            end(403, "wrong password!")
    elif 'Password' in config and config['Password'] != password:
        end(403, "wrong password!")
    elif isTest:
        end(401, "There's no password in server configuration!")


config = read_config()
app = bottle.default_app()


# Bottle routes
@route('/')
def index():
    redirect("https://photobackup.github.io/")


@route('/', method='POST')
def save_image():
    validate_password(request)

    upfile = request.files.get('upfile')
    if not upfile:
        end(401, "no file in the request!")

    filesize = -1
    try:
        filesize = int(request.forms.get('filesize'))
    except TypeError:
        end(400, "Missing file size in the request!")

    # handle file
    path = os.path.join(config['MediaRoot'], upfile.raw_filename)
    if not os.path.exists(path):

        # save file
        info("upfile path: " + path)
        upfile.save(path)

        # check file size in request against written file size
        if filesize != os.stat(path).st_size:
            end(411, "file sizes do not match!")

    elif filesize == os.stat(path).st_size:
        end(409, "file exists and is complete")

    else:
        warn("file " + path + " is incomplete, resaving!")
        upfile.save(path)


@route('/test', method='POST')
def test():
    validate_password(request, True)

    if not os.path.exists(config['MediaRoot']):
        end(500, "'MediaRoot' directory does not exist!")

    testfile = os.path.join(config['MediaRoot'], '.test_file_to_write')
    try:
        with open(testfile, 'w') as tf:
            tf.write('')
    except:
        end(500, "Can't write to 'MediaRoot' directory!")
    finally:
        os.remove(testfile)
        info("Test succeeded \o/")


def main():
    arguments = docopt(__doc__, version='PhotoBackup ' + __version__)
    if (arguments['init']):
        init_config()
    elif (arguments['run']):
        run(port=config['Port'], host=config['BindAddress'])


if __name__ == '__main__':
    main()
