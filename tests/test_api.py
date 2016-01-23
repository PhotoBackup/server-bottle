# stlib
import configparser
import os
# pipped
import requests


# read config file
filename = os.path.expanduser("~/.photobackup")
parser = configparser.ConfigParser()
parser.read_file(open(filename))
config = parser['photobackup']

# stuff we need
url = 'http://' + config['BindAddress'] + ':' + config['Port']
upfile_name = 'test_api.py'
upfile = os.path.join('tests', upfile_name)
upfile_dict = {'upfile': open(upfile, 'rb')}

# clean before testing
file_to_remove = os.path.join(config['MediaRoot'], upfile_name)
try:
    os.remove(file_to_remove)
except FileNotFoundError:
    pass


#########
# Tests #
#########
def test_root200():
    """ Test the simplest route of the server. """
    r = requests.get(url)
    assert r.status_code == 200


def test_nopwd403():
    """ Test the status when posting with no argument. """
    r = requests.post(url)
    assert r.status_code == 403


def test_wrongfile403():
    """ Test the status when posting with a wrong password. """
    payload = {'password': 'WRONG PASSWORD'}
    r = requests.post(url, data=payload)
    assert r.status_code == 403


def test_noupfile401():
    """ Test the status when posting with the right password but no upfile. """
    payload = {'password': config['Password']}
    r = requests.post(url, data=payload)
    assert r.status_code == 401


def test_nofilesize400():
    """ Test the status when posting with the right password, an upfile
        but no file size parameter. """
    payload = {'password': config['Password'] }
    r = requests.post(url, data=payload, files=upfile_dict)
    assert r.status_code == 400

