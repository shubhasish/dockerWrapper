import docker
from tls import TLS

class Network:
    def __init__(self,name,url):
        tls = TLS()
        self.tlsConfig = tls.getTLSconfig(name)

        self.client = docker.DockerClient(base_url=url, tls=self.tlsConfig)

    def create_network(self,name,type):
        try:
            self.client.networks.create(name=name,driver=type)
            return True
        except Exception as e:
            print e
            return False