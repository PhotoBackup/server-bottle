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
import os, errno        # for creating the directory
import sys
try:
    import pwd          # permission checks on *nix systems
except ImportError:
    pass    # bypass the import error for Windows
import stat
# pipped
import bcrypt

# variables
_config_file = os.path.expanduser("~/.photobackup")


def writable_by(dirname, user):
    """ Checks if the given directory is writable by the named user, or the group she belongs to."""

    dir_stat = os.stat(dirname)

    if not stat.S_ISDIR(dir_stat.st_mode):
        print('The {} is not a directory, exiting.'.format(dirname))
        sys.exit(1)

    try:
        pwnam = pwd.getpwnam(user)
    except KeyError:
        print('[ERROR] User or group {0} does not exist!'.format(user))
        return False
    except NameError:
        print('[WARN] Writable verification cannot be performed on non-unix like systems, skipping.')
        return True

    user_id, group_id = pwnam.pw_uid, pwnam.pw_gid
    directory_mode = dir_stat[stat.ST_MODE]
    # The user has to have w, r and x on a directory - to list content, create/modify, and access inodes
    # https://stackoverflow.com/a/46745175/3446126
    
    if user_id == dir_stat[stat.ST_UID] and stat.S_IRWXU & directory_mode == stat.S_IRWXU:     # owner and has RWX
        return True
    elif group_id == dir_stat[stat.ST_GID] and stat.S_IRWXG & directory_mode == stat.S_IRWXG:  # in group & it has RWX
        return True
    elif stat.S_IRWXO & directory_mode == stat.S_IRWXO:                                        # everyone has RWX
        return True

    # no permissions
    return False


def init(section=None):
    """ Initializes the PhotoBackup configuration file. 
    :param section: Optional argument of a custom section to be created in the config file. The generated name
                    will be "[photobackup-section]".
                    The option is useful for having different configurations like staging, production, etc, in the
                    same file, or pseudo multi-tenant environment.
                    If not set, the default "[photobackup]" section is created.
        """
    print("""===============================
PhotoBackup_bottle init process
===============================""")

    # ask for the upload directory (should be writable by the server)
    media_root = input('The directory where to put the pictures (should be writable by the server you use): ')

    if not media_root:
        print('No directory given, stopping.')
        sys.exit(1)

    try:
        os.makedirs(media_root)
        print('Directory {0} did not exist, created it'.format(media_root))
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            print('The directory did not exist, and failed to create it - {} '.format(ex))
            sys.exit(1)

    server_user = input('Owner of the directory [www-data]: ')
    if not server_user:
        server_user = 'www-data'

    check_writable_by = input('Verify the user {0} has write permissions on {1} [Yn]: '
                              .format(server_user, media_root))

    # test for user writability of the directory
    if not check_writable_by or check_writable_by.strip().lower()[0] == 'y':
        if not writable_by(media_root, server_user):
            print('[WARN] Directory {0} is not writable by {1}, check it!'.format(media_root, server_user))

    # ask for the server password
    password = getpass.getpass(prompt='The server password: ')
    pass_sha = hashlib.sha512(
        password.encode('utf-8')).hexdigest().encode('utf-8')
    passhash = bcrypt.hashpw(pass_sha, bcrypt.gensalt())

    # save the config file

    config = configparser.ConfigParser()
    config.optionxform = str  # to keep case of keys
    config.read(_config_file)  # to keep existing data; doesn't file if there's no file yet

    suffix = '-' + section if section else ''
    config_key = 'photobackup' + suffix

    config[config_key] = {'BindAddress': '127.0.0.1',
                          'MediaRoot': media_root,
                          'Password': pass_sha.decode(),
                          'PasswordBcrypt': passhash.decode(),
                          'Port': 8420}

    with open(_config_file, 'w') as configfile:
        config.write(configfile)


def read_config(section=None):
    """ Returns a dictionary with the configuration data, read from the config file.
    :param section: Optional argument of which custom section to read.
                    If not set, the "[photobackup]" section is read."""

    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option  # to keep case of keys
    try:
        if not os.path.isfile(_config_file):
            raise OSError('The configuration file "{}" does not exist'.format(_config_file))
        config.read_file(open(_config_file))
    except EnvironmentError as ex:
        print("Can't read the configuration file - run 'photobackup init'\n{}".format(ex))
        sys.exit(1)

    suffix = '-' + section if section else ''
    config_key = 'photobackup' + suffix

    values = None
    try:
        values = config[config_key]
    except KeyError:
        print("The configuration file does not have {} section".format(config_key))
        sys.exit(1)

    return values


def return_config_sections():
    """ Print the existing PhotoBackup configuration sections; the default is named "<unnamed one>". """

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
