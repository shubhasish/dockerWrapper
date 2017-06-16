import docker
from tls import TLS

class Swarm:
    def __init__(self,name,url):
        tls = TLS()
        self.tlsConfig = tls.getTLSconfig(name)

        self.client = docker.DockerClient(base_url=url,tls=self.tlsConfig)
    def getTokens(self):
        pass

    def swarmInit(self,advertise_addr):
        advertise_addr = advertise_addr + ':2377'
        try:
            output = self.client.swarm.init(advertise_addr=advertise_addr)
            return True
        except Exception as e:
            print e
            return False

    def joinSwarm(self,ip,token,listen):
        ip = ip + ':2377'
        listen = listen + ":2377"
        print ip
        try:
            output = self.client.swarm.join(remote_addrs=[ip],join_token=token,listen_addr=listen)
            return True
        except Exception as e:
            print e
            return False

    # def deployPortnair(self):
    #     try:
    #         self.client.services.create(image='portainer/portainer',name=)

