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
import pwd
import stat
# pipped
import bcrypt


def writable_by(dirname, name, user_or_group):
    """ Checks if the given directory is writable by the named user or group.
        user_or_group is a boolean with True for a user and False for a group. """
    try:
        pwnam = pwd.getpwnam(name)
    except KeyError:
        print('[ERROR] User or group {0} does not exist!'.format(name))
        return False
    ugid = pwnam.pw_uid if user_or_group else pwnam.pw_gid

    dir_stat = os.stat(dirname)
    ug_stat = dir_stat[stat.ST_UID] if user_or_group else dir_stat[stat.ST_GID]
    iw_stat = stat.S_IWUSR if user_or_group else stat.S_IWGRP

    if ((ug_stat == ugid) and (dir_stat[stat.ST_MODE] & iw_stat)):
        return True

    return False


def init(username=None):
    """ Initializes the PhotoBackup configuration file. """
    print("""===============================
PhotoBackup_bottle init process
===============================""")

    # ask for the upload directory (should be writable by the server)
    media_root = input("The directory where to put the pictures" +
                       " (should be writable by the server you use): ")
    try:
        os.mkdir(media_root)
        print("Directory {0} does not exist, creating it".format(media_root))
    except OSError:
        print("Directory already exists")

    # test for user writability of the directory
    server_user = input("Owner of the directory [www-data]: ")
    if not server_user:
        server_user = 'www-data'
    if not writable_by(media_root, server_user, True) and \
            not writable_by(media_root, server_user, False):
        print('[INFO] Directory {0} is not writable by {1}, check it!'
              .format(media_root, server_user))

    # ask a password for the server
    password = getpass.getpass(prompt='The server password: ')
    pass_sha = hashlib.sha512(
        password.encode('utf-8')).hexdigest().encode('utf-8')
    passhash = bcrypt.hashpw(pass_sha, bcrypt.gensalt())

    # save in config file
    config_file = os.path.expanduser("~/.photobackup")
    config = configparser.ConfigParser()
    config.optionxform = str  # to keep case of keys
    config.read(config_file)  # to keep existing data
    suffix = '-' + username if username else ''
    config_key = 'photobackup' + suffix
    config[config_key] = {'BindAddress': '127.0.0.1',
                          'MediaRoot': media_root,
                          'Password': pass_sha.decode(),
                          'PasswordBcrypt': passhash.decode(),
                          'Port': 8420}
    with open(config_file, 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    init()
