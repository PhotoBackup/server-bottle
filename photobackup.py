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
import os
# pipped
from bottle import abort, request, route, run, template
import bottle
from logbook import debug, warn
# local
from photobackup_settings import MEDIA_ROOT, PASSWORD


app = bottle.default_app()


@route('/', method='POST')
def save_image():
    password = request.forms.get('password')
    if password != PASSWORD:
        abort(403, "ERROR: wrong password!")

    upfile = request.files.get('upfile')
    if not upfile:
        abort(401, "ERROR: no file in the request!")

    path = os.path.join(MEDIA_ROOT, upfile.raw_filename)
    if not os.path.exists(path):
        debug("upfile path: " + path)
        upfile.save(path)
    else:
        warn("file " + path + " already exists")


@route('/')
def index():
    return template('index')


@route('/test')
def test():
    password = request.forms.get('password')
    if password != PASSWORD:
        abort(403, "ERROR: wrong password!")

    if not os.path.exists(MEDIA_ROOT):
        abort(500, "ERROR: MEDIA_ROOT does not exist!")

    testfile = os.path.join(MEDIA_ROOT, '.test_file_to_write')
    try:
        with open(testfile, 'w') as tf:
            tf.write('')
    except:
        abort(500, "ERROR: can't write to MEDIA_ROOT!")
    finally:
        os.remove(testfile)


if __name__ == '__main__':
    run(host='0.0.0.0', reloader=True)
