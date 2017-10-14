#!/usr/bin/env python
# Copyright (C) 2013-2016 Stéphane Péchard.
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
  photobackup init [<username>]
  photobackup run [<username>]
  photobackup list
  photobackup (-h | --help)
  photobackup --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# stlib

import os
import sys
from functools import wraps   # better decorators
# pipped
import bcrypt
from bottle import abort, redirect, request, route, run
import bottle
from docopt import docopt
from logbook import Logger, StreamHandler
# local
from . import __version__, serverconfig


# Server functions
def end(code, message):
    """ Aborts the request and returns the given error. """
    log.error(message)
    abort(code, message)


def validate_password(func):
    """ Validates the password given in the request against the stored Bcrypted one. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        password = None
        try:
            password = request.forms.get('password').encode('utf-8')
        except AttributeError:
            end(403, 'No password in request')
        
        passcrypt = config['PasswordBcrypt'].encode('utf-8')
        if not bcrypt.checkpw(password, passcrypt):
            end(403, 'wrong password!')

        return func(*args, **kwargs)

    return wrapper


def save_file(upfile, filesize):
    """ Saves the received file locally. """
    path = os.path.join(config['MediaRoot'], os.path.basename(upfile.raw_filename))
    if not os.path.exists(path):

        # save file
        log.info("upfile path: " + path)
        upfile.save(config['MediaRoot'])

        # check file size in request against written file size
        if filesize != os.stat(path).st_size:
            end(411, "file sizes do not match!")

    elif filesize == os.stat(path).st_size:
        end(409, "file exists and is complete")

    else:
        log.warn("file " + path + " is incomplete, resaving!")
        try:
            os.remove(path)
        except OSError:
            log.info("File already removed, strange but cool...")
        try:
            upfile.save(config['MediaRoot'])
        except OSError:
            log.error("Impossible to save the file...")


# Bottle routes
@route('/')
def index():
    """ Redirects to the PhotoBackup website. """
    redirect("https://photobackup.github.io/")


@route('/', method='POST')
@validate_password
def save_image():
    """ Saves the given image to the directory set in the configured. """
    upfile = request.files.get('upfile')
    if not upfile:
        end(401, "no file in the request!")

    filesize = -1
    try:
        filesize = int(request.forms.get('filesize'))
    except TypeError:
        end(400, "Missing file size in the request!")

    save_file(upfile, filesize)


@route('/test', method='POST')
@validate_password
def test():
    """ Tests the server capabilities to handle a POST requests. """
    if not os.path.exists(config['MediaRoot']):
        end(500, "'MediaRoot' directory does not exist!")

    testfile = os.path.join(config['MediaRoot'], '.test_file_to_write')
    try:
        with open(testfile, 'w') as tf:
            tf.write('')
    except EnvironmentError:
        end(500, "Can't write to 'MediaRoot' directory!")
    finally:
        os.remove(testfile)
        log.info("Test succeeded \o/")


# CLI handlers - they don't use the log, but print()
def init_config(section=None):
    """ Creates the configuration file.
    param section: Optional argument of a custom section that'll be created in the config file.
    """
    serverconfig.init(section)
    print("Created, now launch PhotoBackup server with 'photobackup run'")
    sys.exit(0)


def print_list():
    """ Prints the existing PhotoBackup configuration sections. """
    print(serverconfig.return_config_sections())
    sys.exit(0)


# internal helpers
def _create_logger():
    """ Creates the logger fpr this module. """
    StreamHandler(sys.stdout).push_application()
    return Logger('PhotoBackup')

# variables
arguments = docopt(__doc__, version='PhotoBackup ' + __version__)

# the server configuraiton dict; will be filled-in in main()
config = None

log = _create_logger()


def main():
    """ Prepares and launches the bottle app. """
    if arguments['init']:
        init_config(arguments['<username>'])
        sys.exit(0)

    global config
    config = serverconfig.read_config(arguments['<username>'])

    if arguments['run']:
        app = bottle.default_app()
        if 'HTTPPrefix' in config:
            app.mount(config['HTTPPrefix'], app)
        app.run(port=config['Port'], host=config['BindAddress'])
    elif arguments['list']:
        print_list()


if __name__ == '__main__':
    main()
