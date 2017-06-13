
import docker
import subprocess
from dockerMachine import dockerMachine
import json


###### JSON List
print "Starting the wrapper Application"
jsonFile = open("config.json",'r+')
jsonform = json.loads(jsonFile.read())
jsonFile.close()
requiredMachines  = set(jsonform.keys())


###### Initialization
swarm_init = False
Flag = False
managerToken = None
workerToken = None
swarmIp = None

###### Client Initialization
print "Initializing client"
dockerMachine = dockerMachine()
print "Checking for Existing Machines in Swarm"
existingCluster = dockerMachine.listAvailableMachines()

if len(existingCluster)==0:
    print "No nodes are present in this cluster"
else:
    Flag = True
    print "Following nodes are present in the cluster"
    for node in existingCluster:
        print "%s \t %s"%(node,jsonform[node]['role'])


###### Swarm Initialization
swarmList = set([])
if Flag:
    print "Checking for swarm initialization"
    for node in existingCluster:
        if jsonform[node]['role'].lower() == "manager":

            output = dockerMachine.checkSwarm(node)
            if output[0]:
                print "Swarm token found with node %s" % node
                managerToken = [x for x in output[1] if 'SWMTKN' in x][0]
                workerToken = [x for x in output[2] if 'SWMTKN' in x][0]
                swarmIp = dockerMachine.getIp(node) +':2377'

                swarm_init = True
                # nodesList = dockerMachine.getSwarmNodes(node)
                # print len(nodesList)
                # print nodesList
                # swarmList = [nodesList[i] for i in range(1,len(nodesList),6)]
                # print swarmList
            else:
                print "Swarm check for node %s" % node
                print output[1]

                continue

        else:
            continue


###### Creation Lists
createList = requiredMachines.difference(existingCluster)
if len(createList) > 0:
    print "Following nodes will be created"
    for node in createList:
        print "%s \t %s" % (node, jsonform[node]['role'])
    for node in createList:

        print "Creating the node %s" % node
        dockerMachine.createMachine(name=node, driver=jsonform[node]['driver'])
else:
    print "No new machines to be created"

###### SWARM addition
swarmList = swarmList.union(createList)
if swarm_init:
    print "Swarm already initialized"
    print "Adding new nodes to swarm cluster"
    for nodes in swarmList:
        if jsonform[nodes]['role'].lower() == "manager":
            output = dockerMachine.swarm_join(name=nodes,token=managerToken,ip=swarmIp)
            print output
        else:
            output = dockerMachine.swarm_join(name=nodes, token=workerToken, ip=swarmIp)
            print output
else:
    print "Swarm hasn't been initialized"
    print "Initializing Swarm..."
    swarmMaster = [x for x in createList if jsonform[x]['role'].lower() == "manager"][0]
    print swarmMaster
    swarmIp = dockerMachine.getIp(swarmMaster) + ':2377'
    dockerMachine.swarm_init(swarmMaster,swarmIp)
    masterDetails = dockerMachine.checkSwarm(swarmMaster)
    managerToken = [x for x in masterDetails[1] if 'SWMTKN' in x][0]
    workerToken = [x for x in masterDetails[2] if 'SWMTKN' in x][0]
    swarmList.remove(swarmMaster)
    for nodes in swarmList:
        if jsonform[nodes]['role'].lower() == "manager":
            output = dockerMachine.swarm_join(name=nodes,token=managerToken,ip=swarmIp)
            print output
        else:
            output = dockerMachine.swarm_join(name=nodes, token=workerToken, ip=swarmIp)
            print output
