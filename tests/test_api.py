# stlib
import configparser
import os
# pipped
import pytest
import requests


# read server config file
filename = os.path.expanduser("~/.photobackup")
parser = configparser.ConfigParser()
parser.read_file(open(filename))
config = parser['photobackup']

# stuff we need
prefix = ''
upfile_name = 'test_api.py'
upfile = os.path.join('tests', upfile_name)
url = 'http://' + config['BindAddress'] + ':' + config['Port']
try:
    prefix = config['HTTPPrefix']
except KeyError:
    print("No HTTPPrefix in config")
finally:
    url += prefix
    print("URL = " + url)

# clean before testing
file_to_remove = os.path.join(config['MediaRoot'], upfile_name)
try:
    os.remove(file_to_remove)
except OSError:  # should be FileNotFoundError for Python > 3.2
    print("File does not exist, no need to remove it.")


#########
# Tests #
#########
class TestClass:

    def test_root200(self):
        """ Test the simplest route of the server. """
        r = requests.get(url)
        assert r.status_code == 200

    def test_nopwd403(self):
        """ Test the status when posting with no argument. """
        r = requests.post(url)
        assert r.status_code == 403

    def test_wrongfile403(self):
        """ Test the status when posting with a wrong password. """
        payload = {'password': 'WRONG PASSWORD'}
        r = requests.post(url, data=payload)
        assert r.status_code == 403

    def test_noupfile401(self):
        """ Test the status when posting with right password but no upfile. """
        payload = {'password': config['Password']}
        r = requests.post(url, data=payload)
        assert r.status_code == 401

    def test_nofilesize400(self):
        """ Test the status when posting with the right password, an upfile
            but no file size parameter. """
        payload = {'password': config['Password']}
        r = requests.post(url, data=payload,
                          files={'upfile': open(upfile, 'rb')})
        assert r.status_code == 400

    def test_sendfile200(self):
        """ Test the status when posting with all the right parameters. """
        payload = {
            'password': config['Password'],
            'filesize': os.stat(upfile).st_size
        }
        r = requests.post(url, data=payload,
                          files={'upfile': open(upfile, 'rb')})
        assert r.status_code == 200

    def test_resendfile409(self):
        """ Test the status when reposting with all the right parameters. """
        payload = {
            'password': config['Password'],
            'filesize': os.stat(upfile).st_size
        }
        r = requests.post(url, data=payload,
                          files={'upfile': open(upfile, 'rb')})
        assert r.status_code == 409

    def test_testendpoint(self):
        """ Test the status when posting with the right password, an upfile
            but no file size parameter. """
        payload = {'password': config['Password']}
        r = requests.post(url + '/test', data=payload)
        assert r.status_code == 200

    # def test_dashboard200(self):
    #     """ Test the simplest route of the server. """
    #     r = requests.get(url + '/dashboard')
    #     assert r.status_code == 200
