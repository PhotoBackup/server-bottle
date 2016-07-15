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
import configparser
import os
import sys
# pipped
import bcrypt
from bottle import abort, redirect, request, route, run
import bottle
from docopt import docopt
from logbook import info, warn, error, Logger, StreamHandler
# local
from . import __version__, init


def create_logger():
    """ Creates the logger fpr this module. """
    StreamHandler(sys.stdout).push_application()
    return Logger('PhotoBackup')


def init_config(username=None):
    """ Launch init.py script to create configuration file on user's disk. """
    init.init(username)
    sys.exit("\nCreated, now launch PhotoBackup server with 'photobackup run'")


def print_list():
    """ Print the existing PhotoBackup configurations. """
    sections = '\n'.join(get_config().sections())
    sections = sections.replace('photobackup-', '- ')
    sections = sections.replace('photobackup', '<unnamed one>')
    print('Runnable PhotoBackup configurations are:')
    print(sections)


def read_config(username=None):
    """ Set configuration file data into local dictionnary. """
    config_file = os.path.expanduser("~/.photobackup")
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option  # to keep case of keys
    try:
        config.read_file(open(config_file))
    except EnvironmentError:
        log.error("can't read configuration file, running 'photobackup init'")
        init_config(username)

    suffix = '-' + username if username else ''
    config_key = 'photobackup' + suffix

    values = None
    try:
        values = config[config_key]
    except KeyError:
        values = None
    return values


def end(code, message):
    """ Aborts the request and returns the given error. """
    log.error(message)
    abort(code, message)


def validate_password(request, isTest=False):
    """ Validates the password given in the request
        against the stored Bcrypted one. """
    password = None
    try:
        password = request.forms.get('password').encode('utf-8')
    except AttributeError:
        end(403, "No password in request")

    if 'PasswordBcrypt' in config:
        passcrypt = config['PasswordBcrypt'].encode('utf-8')
        if bcrypt.hashpw(password, passcrypt) != passcrypt:
            end(403, "wrong password!")
    elif 'Password' in config and config['Password'] != password:
        end(403, "wrong password!")
    elif isTest:
        end(401, "There's no password in server configuration!")


def save_file(upfile, filesize):
    """ Saves the sent file locally. """
    path = os.path.join(config['MediaRoot'], upfile.raw_filename)
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
def save_image():
    """ Saves the given image to the parameterized directory. """
    validate_password(request)

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
def test():
    """ Tests the server capabilities to handle POST requests. """
    validate_password(request, True)

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


# variables
arguments = docopt(__doc__, version='PhotoBackup ' + __version__)
log = create_logger()
config = read_config(arguments['<username>'])


def main():
    """ Prepares and launches the bottle app. """
    if (arguments['init']):
        init_config(arguments['<username>'])
    elif (arguments['run']):
        app = bottle.default_app()
        if 'HTTPPrefix' in config:
            app.mount(config['HTTPPrefix'], app)
        app.run(port=config['Port'], host=config['BindAddress'])
    elif (arguments['list']):
        print_list()


if __name__ == '__main__':
    main()
