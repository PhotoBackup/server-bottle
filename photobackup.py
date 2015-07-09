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
from logbook import info, warn, error
# local
from photobackup_settings import MEDIA_ROOT, PASSWORD


app = bottle.default_app()


def end(code, message):
    error(message)
    abort(code, message)


@route('/')
def index():
    return template('index.html')


@route('/', method='POST')
def save_image():
    password = request.forms.get('password')
    if password != PASSWORD:
        end(403, "wrong password!")

    upfile = request.files.get('upfile')
    if not upfile:
        end(401, "no file in the request!")

    path = os.path.join(MEDIA_ROOT, upfile.raw_filename)
    if not os.path.exists(path):
        filesize = -1
        try:
            filesize = int(request.forms.get('filesize'))
        except TypeError:
            end(400, "missing file size in the request!")

        # save file
        info("upfile path: " + path)
        upfile.save(path)

        # check file size in request against written file size
        if filesize != os.stat(path).st_size:
            end(411, "file sizes do not match!")

    else:
        warn("file " + path + " already exists")


@route('/test', method='POST')
def test():
    password = request.forms.get('password')
    if password != PASSWORD:
        end(403, "wrong password!")

    if not os.path.exists(MEDIA_ROOT):
        end(500, "MEDIA_ROOT does not exist!")

    testfile = os.path.join(MEDIA_ROOT, '.test_file_to_write')
    try:
        with open(testfile, 'w') as tf:
            tf.write('')
    except:
        end(500, "Can't write to MEDIA_ROOT!")
    finally:
        os.remove(testfile)
        info("Test succeeded \o/")


if __name__ == '__main__':
    run(reloader=True)
