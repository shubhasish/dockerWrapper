from urllib2 import Request, urlopen, URLError
import docker

class Swarm(object):
    def __init__(self):
        pass

    def getSwarmToken(self,url):
        client =""

    def swarmInit(self,url):
        client = docker.DockerClient(base_url=url.strip())
        print url.replace('tcp://','')
        try:
            return client.swarm.init(advertise_addr=url.replace('tcp://',''))

        except Exception as e:
            print e
            return False
    def swarmJoin(self,object):
        master_url = object['master']
        slave_url = object['slave']
        token = object['token']
        client = docker.DockerClient(base_url=slave_url)
        client.swarm.join(remote_addrs=[master_url],token=token,advertise_addr=slave_url.replace('tcp://',''))