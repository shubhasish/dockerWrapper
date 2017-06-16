import json
import os
import copy
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config import CONFIG_FORMATT
from wrapper.components.dockerMachine import dockerMachine
from wrapper.components.fileFormatter import File
from wrapper.components.swarm import Swarm

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


MASTER = {}
requiredMachines = createList = existingCluster = memory = configuration = swarm_init = managerToken = workerToken = masterNode = swarmIp = ''
file = File()
dockerMachine = dockerMachine()


def createMachines(createList):

    if len(createList) > 0:
        print "Following nodes will be created"
        master = []
        for node in createList:
            print "%s \t %s" % (node, configuration[node]['role'])
        for node in createList:
            print "Creating the node %s" % node
            dockerMachine.createMachine(name=node, driver=configuration[node]['driver'])
            config = CONFIG_FORMATT
            config['url'] = dockerMachine.getURL(node)
            config['ip'] = dockerMachine.getIp(node)
            config['role'] = configuration[node]['role']
            config['driver'] = configuration[node]['driver']
            MASTER[node] =copy.deepcopy(config)
        print MASTER

    else:
        print "No new machines to be created"



###### File Reading
try:
    print "Starting the wrapper Application"
    configuration = file.readFile('config.json')
    requiredMachines = set(configuration.keys())
except Exception as e:
    print e
    os._exit(1)
try:
    MASTER = file.readFile('shape.memory')
    existingCluster = set(MASTER.keys())
except Exception as e:
    print e

######

if len(existingCluster)==0:
    print "No nodes are present in this cluster"
    createList = requiredMachines
    createMachines(createList)
    swarmList = createList
else:
    print "Following nodes are present in the cluster"
    for node in existingCluster:
        print "%s \t %s"%(node,configuration[node]['role'])
    createList = requiredMachines.difference(existingCluster)
    createMachines(createList)
    swarmList= set([x for x in existingCluster if MASTER[x]['swarm'] == False])
    masterNode = [x for x in existingCluster if MASTER[x]['init'] == True]
##### Swarm Initialization

    if len(masterNode) > 0:
        print "Swarm has been initialized"


        print "Obtaining join token for %s"%masterNode[0]
        output = dockerMachine.checkSwarm(masterNode[0])
        managerToken = [x for x in output[1] if 'SWMTKN' in x][0]
        workerToken = [x for x in output[2] if 'SWMTKN' in x][0]
        swarmIp = MASTER[masterNode[0]]['ip']
        swarm_init = True
    else:
        print "Swarm hasn't been initialized"
        swarm_init = False




###### SWARM addition
print createList,swarmList
swarmList = createList.union(swarmList)
if swarm_init:
    print "Swarm already initialized"
    print "Adding new nodes to swarm cluster"
    print swarmList
    for nodes in swarmList:
        swarm = Swarm(nodes, MASTER[nodes]['url'])
        if configuration[nodes]['role'].lower() == "manager":

            swarm.joinSwarm(ip=swarmIp,token=managerToken,listen=MASTER[nodes]['ip'])
        else:
            swarm.joinSwarm(ip=swarmIp, token=workerToken,listen=MASTER[nodes]['ip'])
else:
    print "Initializing Swarm..."
    print swarmList
    master = [x for x in swarmList if MASTER[x]['role'].lower() == "manager"][0]

    swarmMaster = Swarm(name=master,url=MASTER[master]['url'])
    swarmMaster.swarmInit(MASTER[master]['ip'])
    MASTER[master]['swarm'] = True
    MASTER[master]['init'] = True
    masterDetails = dockerMachine.checkSwarm(master)
    managerToken = [x for x in masterDetails[1] if 'SWMTKN' in x][0]
    workerToken = [x for x in masterDetails[2] if 'SWMTKN' in x][0]
    swarmList.remove(master)
    for nodes in swarmList:
        swarm = Swarm(nodes, MASTER[nodes]['url'])
        if configuration[nodes]['role'].lower() == "manager":

            swarm.joinSwarm(ip=MASTER[master]['ip'], token=managerToken,listen=MASTER[nodes]['ip'])
            MASTER[nodes]['swarm'] = True
        else:
            swarm.joinSwarm(ip=MASTER[master]['ip'], token=workerToken,listen=MASTER[nodes]['ip'])
            MASTER[nodes]['swarm'] = True

if len(MASTER.keys())>0:
    file.writeFile(MASTER)