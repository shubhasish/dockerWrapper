from ..modules.swarm import Swarm
from ..modules.dockerMachine import dockerMachine
class Swarm_Handler:
    def __init__(self):
        self.dockerMachine = dockerMachine()
    def create_swarm(self,swarmlist,dict):
        pass
    def swarm_init(self,masterTuple):
        # print "Initializing Swarm..."
        # master = [x for x in swarmList if MASTER[x]['role'].lower() == "manager"][0]

        swarmMaster = Swarm(name=masterTuple[0], url=masterTuple[1])
        swarmMaster.swarmInit(advertise_addr=masterTuple[2])
        return self.getJoinToken(masterTuple[0])
        # MASTER[master]['swarm'] = True
        # MASTER[master]['init'] = True
        # swarmMaster.create_network('icarus', 'overlay')
        # dockerMachine.deploy_portainer(master)
        # masterDetails = dockerMachine.checkSwarm(master)
        # managerToken = [x for x in masterDetails[1] if 'SWMTKN' in x][0]
        # workerToken = [x for x in masterDetails[2] if 'SWMTKN' in x][0]
        # swarmList.remove(master)
        # for nodes in swarmList:
        #     swarm = Swarm(nodes, MASTER[nodes]['url'])
        #     if configuration[nodes]['role'].lower() == "manager":
        #
        #         swarm.joinSwarm(ip=MASTER[master]['ip'], token=managerToken, listen=MASTER[nodes]['ip'])
        #         MASTER[nodes]['swarm'] = True
        #     else:
        #         swarm.joinSwarm(ip=MASTER[master]['ip'], token=workerToken, listen=MASTER[nodes]['ip'])
        #         MASTER[nodes]['swarm'] = True
    def swarm_join(self,serverlist,tokenList):

        pass
    def getJoinToken(self,master):
        masterDetails = self.dockerMachine.checkSwarm(master)
        managerToken = [x for x in masterDetails[1] if 'SWMTKN' in x][0]
        workerToken = [x for x in masterDetails[2] if 'SWMTKN' in x][0]
        return (managerToken,workerToken)