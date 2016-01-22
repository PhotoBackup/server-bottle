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


#########
# Tests #
#########
def test_root200():
    r = requests.get(url)
    assert r.status_code == 200


def test_nopwd403():
    r = requests.post(url)
    assert r.status_code == 403


def test_wrongfile403():
    payload = {'password': 'WRONG PASSWORD'}
    r = requests.post(url, data=payload)
    assert r.status_code == 403


def test_noupfile(capsys):
    payload = {'password': config['PasswordBcrypt']}
    print(payload)
    r = requests.post(url, data=payload)
    assert r.status_code == 401


