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
            'manage':'/v1/api/wrapper/manage',
            'monitor':'/v1/api/wrapper/monitor',
            'create':'/v1/api/wrapper/create',
            'swarm':'/v1/api/wrapper/swarm',
            'wrapup':'/v1/api/wrapper/wrapup',
            'node_list':'/v1/api/wrapper/nodes',
            'node_update':'/v1/api/wrapper/nodes/update',
            'node_get':'/v1/api/wrapper/nodes/get',
            'service_list':'/v1/api/wrapper/service',
            'service_get':'/v1/api/wrapper/service/<name>',
            'service_task':'/v1/api/wrapper/service/tasks/<name>',
            'service_update':'/v1/api/wrapper/service/update',
            'service_remove':'/v1/api/wrapper/service/remove',
            'build':'/v1/api/wrapper/image/build',
            'registry':'/v1/api/wrapper/registry',
            'image_push':'/v1/api/wrapperimage/push'}

WRAPPER_DB_PATH = expanduser('~')+"/.wrapper/key_value/wrapper.db"
DOCKER_FILE_PATH = expanduser('~')+ "/.wrapper/build/"
DEPLOYMENT_FILE_PATH = expanduser('~')+ "/.wrapper/deploy/"


def getClient(name, url):
    tls = TLS()
    tlsConfig = tls.getTLSconfig(name)

    return docker.DockerClient(base_url=url, tls=tlsConfig)