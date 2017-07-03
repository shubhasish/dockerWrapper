from os.path import expanduser
import os
from modules.tls import TLS
import docker

DEFAULT_HOME_PATH = expanduser('~') + '/.docker/machine/machines/%s/'
CA_PATH = DEFAULT_HOME_PATH + 'ca.pem'
CERT_PATH = DEFAULT_HOME_PATH + 'cert.pem'
KEY_PATH = DEFAULT_HOME_PATH + 'key.pem'
dir_path = os.path.dirname(os.path.realpath(__file__))
DM_URL = "/usr/local/bin/docker-machine"
CONFIG_FORMATT = {"url":"",
                  "ip":"",
                  "role" : "",
                  "driver":"",
                  "init": False,
                  "swarm": False}


def getClient(name, url):
    tls = TLS()
    tlsConfig = tls.getTLSconfig(name)

    return docker.DockerClient(base_url=url, tls=tlsConfig)