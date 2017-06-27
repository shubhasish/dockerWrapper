from machine import Machine
import os
from wrapper.config import dir_path
cmdJson={"join-token_manager":"docker swarm join-token manager",
         "join-token_worker":"docker swarm join-token worker",
         "join":"docker swarm join --token %s %s",
         "init": "docker swarm init --advertise-addr %s",
         "nodes_list":"docker node ls",
         "portainer":"docker service create \
--name portainer \
--publish 9000:9000 \
--constraint 'node.role == manager' \
--mount type=bind,src=//var/run/docker.sock,dst=/var/run/docker.sock \
portainer/portainer \
-H unix:///var/run/docker.sock",
         "registry":"docker service create --name registry --publish 5000:5000 registry:2",
         "stack_deploy":"docker stack deploy --compose-file ~/docker-compose.yml emq",
         "stack_remove":"docker stack rm emq"}

class dockerMachine:
    def __init__(self):
        self.clientUrl = "/usr/local/bin/docker-machine"
        self.client = Machine(path=self.clientUrl)

    def createMachine(self,name,driver="virtualbox"):
        try:
            self.client.create(name=name,driver=driver)
            return True
        except Exception as e:
            print e
            os._exit(1)
    def listAvailableMachines(self):
        return set([x['Name'] for x in self.client.ls() if len(x['Name']) > 0])

    def checkSwarm(self,name):
        try:
            managerToken = self.client.ssh(name,cmd=cmdJson['join-token_manager'])
            workerToken = self.client.ssh(name,cmd=cmdJson['join-token_worker'])
            return (True,managerToken,workerToken)
        except Exception as e:
            return (False,e.message)

    def swarm_join(self,name,token,ip):
        try:
            cmd = cmdJson['join']%(token,ip)
            self.client.ssh(name,cmd=cmd)
        except Exception as e:
            print e

    def getIp(self,name):
        return self.client.ip(name)

    def getURL(self,name):
        return self.client.url(name)

    def getSwarmNodes(self,name):
        return self.client.ssh(name,cmd=cmdJson['nodes_list'])
    def swarm_init(self,name,ip):
        try:
            cmd = cmdJson['init']%(ip)
            self.client.ssh(name,cmd=cmd)
        except Exception as e:
            print e
    def deploy_portainer(self,name):
        try:
            self.client.ssh(name,cmd=cmdJson['portainer'])
            return True
        except Exception as e:
            print e
            return False
    def deploy_registry(self,name):
        try:
            self.client.ssh(name, cmd=cmdJson['registry'])
            return True
        except Exception as e:
            print e
            return False

    def deploy_stack(self,name):
        try:
            self.client.ssh(name,cmd=cmdJson['stack_deploy'])
            return True
        except Exception as e:
            print e
            return False
    def remove_stack(self,name):
        try:
            self.client.ssh(name,cmd=cmdJson['stack_remove'])
            return True
        except Exception as e:
            print e
            return False

    def remove_nodes(self,name):
        try:
            self.client.rm(machine=name)
        except Exception as e:
            print e
    def copy_composeFile(self):
        try:
            self.client.scp(source=dir_path+'/composer/docker-compose.yml',destination='master:~')
        except Exception as e:
            print e