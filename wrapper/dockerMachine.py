from machine import Machine

cmdJson={"join-token_manager":"docker swarm join-token manager",
         "join-token_worker":"docker swarm join-token worker",
         "join":"docker swarm join --token %s %s",
         "init": "docker swarm init --advertise-addr %s",
         "nodes_list":"docker node ls"}

class dockerMachine:
    def __init__(self):
        self.clientUrl = "/usr/local/bin/docker-machine"
        self.client = Machine(path=self.clientUrl)

    def createMachine(self,name,driver="virtualbox"):
        return self.client.create(name=name,driver=driver)

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

    def getSwarmNodes(self,name):
        return self.client.ssh(name,cmd=cmdJson['nodes_list'])
    def swarm_init(self,name,ip):
        try:
            cmd = cmdJson['init']%(ip)
            self.client.ssh(name,cmd=cmd)
        except Exception as e:
            print e
