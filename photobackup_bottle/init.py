#!/usr/bin/env python3
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

# stlib
import configparser
import getpass
import hashlib
import os
import pwd
import stat
# pipped
import bcrypt


def writable_by_user(dirname, username):
    uid = 0
    try:
        uid = pwd.getpwnam(username).pw_uid
    except KeyError:
        print('[ERROR] User {} does not exist!'.format(username))
        return False

    dir_stat = os.stat(dirname)
    if ((dir_stat[stat.ST_UID] == uid) and
            (dir_stat[stat.ST_MODE] & stat.S_IWUSR)):
        return True

    return False


def writable_by_group(dirname, groupname):
    gid = 0
    try:
        gid = pwd.getpwnam(groupname).pw_gid
    except KeyError:
        print('[ERROR] Group {} does not exist!'.format(groupname))
        return False

    dir_stat = os.stat(dirname)
    if ((dir_stat[stat.ST_GID] == gid) and
            (dir_stat[stat.ST_MODE] & stat.S_IWGRP)):
        return True

    return False


def init():
    print("""===============================
PhotoBackup_bottle init process
===============================""")

    # ask for the upload directory (should be writable by the server)
    media_root = input("The directory where to put the pictures" +
                       " (should be writable by the server you use): ")
    if not os.path.isdir(media_root):
        print("Directory {} does not exist, creating it".format(media_root))
        os.mkdir(media_root)

    # test for user writability of the directory
    server_user = input("Owner of the directory [www-data]: ")
    if not server_user:
        server_user = 'www-data'
    if not writable_by_user(media_root, server_user) and \
            not writable_by_group(media_root, server_user):
        print('[INFO] Directory {} is not writable by {}, check it!'
              .format(media_root, server_user))

    # ask a password for the server
    password = getpass.getpass(prompt='The server password: ')
    pass_sha = hashlib.sha512(
        password.encode('utf-8')).hexdigest().encode('utf-8')
    passhash = bcrypt.hashpw(pass_sha, bcrypt.gensalt())

    # save in config file
    config = configparser.ConfigParser()
    config.optionxform = str  # to keep case of keys
    config['photobackup'] = {'BindAddress': '127.0.0.1',
                             'MediaRoot': media_root,
                             'Password': pass_sha.decode(),
                             'PasswordBcrypt': passhash.decode(),
                             'Port': 8420}
    with open(os.path.expanduser("~/.photobackup"), 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    init()
