#!/usr/bin/env python3
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

""" PhotoBackup Python server initialization module.

    It asks the user for configuration and writes it
    to a .ini file.
"""

# stlib
import configparser
import getpass
import hashlib
import os
import sys
try:
    import pwd
except ImportError:
    pass    # bypass the import error for Windows

import stat
# pipped
import bcrypt

# variables
_config_file = os.path.expanduser("~/.photobackup")


def writable_by(dirname, name, user_or_group):
    """ Checks if the given directory is writable by the named user or group.
        user_or_group is a boolean with True for a user and False for a group. """
    # TODO combine user & group in one check...
    try:
        pwnam = pwd.getpwnam(name)
    except KeyError:
        print('[ERROR] User or group {0} does not exist!'.format(name))
        return False
    except NameError:
        print('[WARN] Write verify cannot be performed on non-unix like systems, skipping.')
        return True

    ugid = pwnam.pw_uid if user_or_group else pwnam.pw_gid

    dir_stat = os.stat(dirname)
    ug_stat = dir_stat[stat.ST_UID] if user_or_group else dir_stat[stat.ST_GID]
    iw_stat = stat.S_IWUSR if user_or_group else stat.S_IWGRP

    if (ug_stat == ugid) and (dir_stat[stat.ST_MODE] & iw_stat):
        return True

    return False


def init(username=None):
    """ Initializes the PhotoBackup configuration file. """
    print("""===============================
PhotoBackup_bottle init process
===============================""")

    # ask for the upload directory (should be writable by the server)
    media_root = input('The directory where to put the pictures (should be writable by the server you use): ')
    try:
        os.mkdir(media_root)
        print('Directory {0} did not exist, created it'.format(media_root))
    except OSError:
        print('Directory already exists')

    server_user = input('Owner of the directory [www-data]: ')
    if not server_user:
        server_user = 'www-data'

    check_writable_by = input('Verify the user {0} has write permissions on {1}? [Yn]'
                              .format(server_user, media_root))

    # test for user writability of the directory
    if not check_writable_by or check_writable_by.strip().lower()[0] == 'y':
        if not writable_by(media_root, server_user, True) and not writable_by(media_root, server_user, False):
            print('[WARN] Directory {0} is not writable by {1}, check it!'.format(media_root, server_user))

    # ask a password for the server
    password = getpass.getpass(prompt='The server password: ')
    pass_sha = hashlib.sha512(
        password.encode('utf-8')).hexdigest().encode('utf-8')
    passhash = bcrypt.hashpw(pass_sha, bcrypt.gensalt())

    # save in config file

    config = configparser.ConfigParser()
    config.optionxform = str  # to keep case of keys
    config.read(_config_file)  # to keep existing data; doesn't file if there's no file yet

    suffix = '-' + username if username else ''
    config_key = 'photobackup' + suffix

    config[config_key] = {'BindAddress': '127.0.0.1',
                          'MediaRoot': media_root,
                          'Password': pass_sha.decode(),
                          'PasswordBcrypt': passhash.decode(),
                          'Port': 8420}

    with open(_config_file, 'w') as configfile:
        config.write(configfile)


def read_config(username=None):
    """ Returns a dictionary with the configuration data, read from the config file. """

    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option  # to keep case of keys
    try:
        if not os.path.isfile(_config_file):
            raise OSError('The configuration file "{}" does not exist'.format(_config_file))
        config.read_file(open(_config_file))
    except EnvironmentError as ex:
        print("Can't read the configuration file - run 'photobackup init'\n{}".format(ex))
        sys.exit(1)

    suffix = '-' + username if username else ''
    config_key = 'photobackup' + suffix

    values = None
    try:
        values = config[config_key]
    except KeyError:
        print("The configuration file does not have {} section".format(config_key))
        sys.exit(1)

    return values


def return_config_sections():
    """ Print the existing PhotoBackup configurations. """

    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option  # to keep case of keys

    try:
        config.read_file(open(_config_file))
    except EnvironmentError as ex:
        print("Cannot read the configuration file - {}".format(ex))
        sys.exit(1)

    sections = '\n'.join(config.sections())
    sections = sections.replace('photobackup-', '')
    sections = sections.replace('photobackup', '<unnamed one>')

    return 'Runnable PhotoBackup configurations are: \n{}'.format(sections)


if __name__ == '__main__':
    init()
