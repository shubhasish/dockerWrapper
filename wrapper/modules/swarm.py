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

    def create_network(self,name, type):
        try:
            self.client.networks.create(name=name,driver=type)
            return True
        except Exception as e:
            print e
            return False

#     def deploy_portnair(self):
#         image = 'portainer/portainer'
#         name = 'portainer'
#         command = ['-H','unix:///var/run/docker.sock']
#         arguments =[]
#         mounts = ['/var/run/dockr.sock:/var/run/dockr.sock']
# #        constraints = ['node.role == manager']
# #        endpoint_spec = docker.types.EndpointSpec(mode='vip',ports={9000:9000})
#         try:
#             self.client.services.create(image=image,name=name,command=command,mounts=mounts)#,constraints=constraints,endpoint_spec=endpoint_spec)
#         except Exception as e:
#             print e
#
# import requests
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#
# client = Swarm(name='master',url='tcp://192.168.99.100:2376')
# client.deploy_portnair()
