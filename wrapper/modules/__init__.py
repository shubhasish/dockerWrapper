
from machine import Machine

import docker
from tls import TLS


def getClient(name, url):
    tls = TLS()
    tlsConfig = tls.getTLSconfig(name)

    return docker.DockerClient(base_url=url, tls=tlsConfig)

machine = Machine("/usr/local/bin/docker-machine")
masterMachine = getClient("master","tcp://192.168.99.100:2376")
machine.scp('../composer/telegraf.conf','master:~')
