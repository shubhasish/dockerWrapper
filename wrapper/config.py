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

API_DICT = {'shutdown':'/v1/api/wrapper/shutdown',
            'deploy':'/v1/api/wrapper/deploy',
            'redeploy':'/v1/api/wrapper/re-deploy',
            'monitor':'/v1/api/wrapper/monitor',
            'create':'/v1/api/wrapper/create',
            'swarm':'/v1/api/wrapper/swarm',
            'wrapup':'/v1/api/wrapper/wrapup',
            'node_list':'/v1/api/wrapper/nodes',
            'node_update':'/v1/api/nodes/update',
            'node_get':'/v1/api/nodes/get',
            'service_list':'/v1/api/service',
            'service_get':'/v1/api/service/<name>',
            'service_task':'/v1/api/service/tasks/<name>',
            'service_update':'/v1/api/service/update',
            'service_remove':'/v1/api/service/remove/<name>',
            'build':'/v1/api/image/build'}

WRAPPER_DB_PATH = expanduser('~')+"/.wrapper/key_value/wrapper.db"

def getClient(name, url):
    tls = TLS()
    tlsConfig = tls.getTLSconfig(name)

    return docker.DockerClient(base_url=url, tls=tlsConfig)