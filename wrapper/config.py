from os.path import expanduser
import os

DEFAULT_HOME_PATH = expanduser('~') + '/.docker/machine/machines/%s/'
CA_PATH = DEFAULT_HOME_PATH + 'ca.pem'
CERT_PATH = DEFAULT_HOME_PATH + 'cert.pem'
KEY_PATH = DEFAULT_HOME_PATH + 'key.pem'
dir_path = os.path.dirname(os.path.realpath(__file__))

CONFIG_FORMATT = {"url":"",
                  "ip":"",
                  "role" : "",
                  "driver":"",
                  "init": False,
                  "swarm": False}