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

# stlib
import getpass
import hashlib
import os
import pwd
import shutil
import sys
# pipped
from logbook import notice, warn


def create_settings_file():
    filename = 'photobackup_settings.py'
    global input

    # Python2 compatibility for input()
    try:
        input = raw_input
    except NameError:
        pass

    # ask for the upload directory (should be writable by the server)
    media_root = input("The directory where to put the pictures" +
                       " (should be writable by the server you use): ")
    if not os.path.isdir(media_root):
        notice("Directory {} does not exist, creating it".format(media_root))
        os.mkdir(media_root)
    server_user = input("Owner of the directory [www-data]: ")
    if not server_user:
        server_user = 'www-data'

    try:
        server_user_uid = pwd.getpwnam(server_user).pw_uid
        if os.stat(media_root).st_uid != server_user_uid:
            notice("Changing owner to: ".format(server_user))
            try:
                shutil.chown(media_root, server_user, server_user)
            except AttributeError:
                warn("Can't change directory's owner, please do it correctly!")
    except KeyError:
        warn("User {} not found, please check the directory's rights."
             .format(server_user))

    # ask a password for the server
    text = "The server password that you use in the mobile app: "
    password = getpass.getpass(prompt=text)
    passhash = hashlib.sha512(password.encode('utf-8')).hexdigest()

    with open(filename, 'w') as settings:
        settings.write("# generated settings for PhotoBackup Bottle server\n")
        settings.write("MEDIA_ROOT = '{}'\n".format(media_root))
        settings.write("PASSWORD = '{}'\n".format(passhash))

    notice("Settings file is created, please launch me again!")
    return media_root, passhash

MEDIA_ROOT, PASSWORD = None, None

# import user-created settings for this specific server
try:
    from photobackup_settings import MEDIA_ROOT, PASSWORD
    if os.path.isdir(MEDIA_ROOT) and os.path.exists(MEDIA_ROOT):
        notice("pictures directory is " + MEDIA_ROOT)
    else:
        sys.exit("pictures directory " + MEDIA_ROOT + "does not exist!")
except ImportError:
    warn("Can't find photobackup_settings.py file, creating it")
    MEDIA_ROOT, PASSWORD = create_settings_file()
