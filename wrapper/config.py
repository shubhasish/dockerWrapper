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

API_DICT = {'shutdown':'/v2/api/wrapper/shutdown',
            'deploy':'/v2/api/wrapper/deploy',
            'redeploy':'/v2/api/wrapper/re-deploy',
            'manage':'/v2/api/wrapper/manage',
            'monitor':'/v2/api/wrapper/monitor',
            'create':'/v2/api/wrapper/create',
            'swarm':'/v2/api/wrapper/swarm',
            'wrapup':'/v2/api/wrapper/wrapup',
            'node_list':'/v2/api/wrapper/nodes',
            'node_update':'/v2/api/wrapper/nodes/update',
            'node_get':'/v2/api/wrapper/nodes/get',
            'service_list':'/v2/api/wrapper/service',
            'service_get':'/v2/api/wrapper/service/<name>',
            'service_task':'/v2/api/wrapper/service/tasks/<name>',
            'service_update':'/v2/api/wrapper/service/update',
            'service_remove':'/v2/api/wrapper/service/remove',
            'hori_scale':'/v2/api/wrapper/horiscale'}

WRAPPER_DB_PATH = expanduser('~')+"/.wrapper/key_value/wrapper.db"
DOCKER_FILE_PATH = expanduser('~')+ "/.wrapper/build/"
DEPLOYMENT_FILE_PATH = expanduser('~')+ "/.wrapper/deploy/"
TELEGRAF_FILE_PATH = expanduser('~')+ "/.wrapper/telegraf/"


def getClient(name, url):
    tls = TLS()
    tlsConfig = tls.getTLSconfig(name)

    return docker.DockerClient(base_url=url, tls=tlsConfig)